"""
SportAI Suite — Foundation Card CRM Router
Sprint 2 · Level Playing Field Foundation
Member pipeline: Individual $249, Family $399, Corporate $149–$199
Target: 1,350 → 4,500 members · $416K/yr revenue

Add to main.py:
    from routers.foundation_card import router as foundation_card_router
    app.include_router(foundation_card_router)
"""

from __future__ import annotations

import enum
import uuid
from datetime import date, datetime, timedelta
from typing import Optional

from anthropic import Anthropic
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import (
    Boolean, Column, Date, DateTime, Enum as SAEnum,
    Float, ForeignKey, Integer, String, Text, func, select, and_
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from database import get_db

class Base(DeclarativeBase):
    pass

# ── Enums ─────────────────────────────────────────────────────────────────────

class CardTier(str, enum.Enum):
    INDIVIDUAL  = "individual"    # $249/yr
    FAMILY      = "family"        # $399/yr
    CORPORATE   = "corporate"     # $149–$199/yr (sponsorship-linked)
    CHARTER     = "charter"       # Founding member / legacy rate

class MemberStatus(str, enum.Enum):
    ACTIVE    = "active"
    EXPIRED   = "expired"
    CANCELLED = "cancelled"
    TRIAL     = "trial"
    PENDING   = "pending"

class RedemptionType(str, enum.Enum):
    EQUIPMENT_DISCOUNT   = "equipment_discount"
    COURT_CREDIT         = "court_credit"
    CAMP_DISCOUNT        = "camp_discount"
    EVENT_ACCESS         = "event_access"
    SCHOLARSHIP_REFERRAL = "scholarship_referral"
    RETAIL_DISCOUNT      = "retail_discount"
    GUEST_PASS           = "guest_pass"
    PRIORITY_BOOKING     = "priority_booking"

class RenewalRisk(str, enum.Enum):
    LOW      = "low"
    MEDIUM   = "medium"
    HIGH     = "high"
    CRITICAL = "critical"

# ── Tier config ───────────────────────────────────────────────────────────────

TIER_PRICING = {
    CardTier.INDIVIDUAL: 249.0,
    CardTier.FAMILY:     399.0,
    CardTier.CORPORATE:  174.0,   # midpoint of $149–$199
    CardTier.CHARTER:    199.0,   # legacy rate
}

TIER_BENEFITS = {
    CardTier.INDIVIDUAL: [
        "Unlimited open-play access all 8 sports",
        "10% discount at Replay Sports Store",
        "Priority booking window (48hr advance)",
        "2 guest passes/month",
        "NIL program eligibility",
        "Scholarship referral eligibility",
    ],
    CardTier.FAMILY: [
        "All Individual benefits (up to 6 family members)",
        "15% discount at Replay Sports Store",
        "Priority booking window (72hr advance)",
        "4 guest passes/month",
        "Free equipment rental (1 item/week)",
        "Youth camp registration priority",
    ],
    CardTier.CORPORATE: [
        "Named corporate sponsor recognition",
        "10 employee membership access passes",
        "Logo on NXS community board",
        "VIP event invitations",
        "Sponsor Exposure Counter impressions tracked",
        "Annual impact report naming",
    ],
    CardTier.CHARTER: [
        "All Individual benefits + permanent legacy pricing",
        "Founding member recognition plaque",
        "Guaranteed renewal at $199/yr regardless of future increases",
        "Monthly leadership briefings with Shaun Marline",
    ],
}

# ── ORM Models ────────────────────────────────────────────────────────────────

class FoundationCardMember(Base):
    """Foundation Card member — the LPF community membership program."""
    __tablename__ = "foundation_card_members"

    id: Mapped[str]              = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name: Mapped[str]      = mapped_column(String(100), nullable=False)
    last_name: Mapped[str]       = mapped_column(String(100), nullable=False)
    email: Mapped[str]           = mapped_column(String(255), nullable=False, unique=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    tier: Mapped[str]            = mapped_column(SAEnum(CardTier), nullable=False)
    status: Mapped[str]          = mapped_column(SAEnum(MemberStatus), default=MemberStatus.ACTIVE)
    annual_fee: Mapped[float]    = mapped_column(Float, nullable=False)
    member_since: Mapped[date]   = mapped_column(Date, nullable=False)
    expiry_date: Mapped[date]    = mapped_column(Date, nullable=False)
    renewal_risk: Mapped[str]    = mapped_column(SAEnum(RenewalRisk), default=RenewalRisk.LOW)
    # Family/corporate extras
    family_size: Mapped[int]     = mapped_column(Integer, default=1)
    company_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    # Engagement metrics
    redemptions_ytd: Mapped[int]  = mapped_column(Integer, default=0)
    visits_ytd: Mapped[int]       = mapped_column(Integer, default=0)
    last_activity_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    # Pipeline tracking
    referral_source: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    referred_by_id: Mapped[Optional[str]]  = mapped_column(String(36), nullable=True)
    notes: Mapped[Optional[str]]           = mapped_column(Text, nullable=True)
    is_active: Mapped[bool]                = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime]           = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime]           = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    redemptions: Mapped[list["CardRedemption"]] = relationship("CardRedemption", back_populates="member", cascade="all, delete-orphan")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def days_until_expiry(self) -> int:
        return (self.expiry_date - date.today()).days

    @property
    def is_expiring_soon(self) -> bool:
        return 0 < self.days_until_expiry <= 60

    @property
    def engagement_score(self) -> float:
        """0–100 engagement score based on visits + redemptions."""
        visit_score = min(self.visits_ytd / 52 * 60, 60)      # max 60 pts from weekly visits
        redemption_score = min(self.redemptions_ytd / 12 * 40, 40)  # max 40 pts from monthly redemptions
        return round(visit_score + redemption_score, 1)

class CardRedemption(Base):
    """Individual benefit redemption event."""
    __tablename__ = "card_redemptions"

    id: Mapped[str]                      = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    member_id: Mapped[str]               = mapped_column(ForeignKey("foundation_card_members.id"), nullable=False)
    redemption_type: Mapped[str]         = mapped_column(SAEnum(RedemptionType), nullable=False)
    value_redeemed: Mapped[float]        = mapped_column(Float, default=0.0)   # $ value of benefit used
    notes: Mapped[Optional[str]]         = mapped_column(Text, nullable=True)
    redemption_date: Mapped[date]        = mapped_column(Date, default=date.today)
    created_at: Mapped[datetime]         = mapped_column(DateTime(timezone=True), server_default=func.now())

    member: Mapped["FoundationCardMember"] = relationship("FoundationCardMember", back_populates="redemptions")

class CardTierConfig(Base):
    """Live tier configuration — prices and member counts."""
    __tablename__ = "card_tiers"

    id: Mapped[str]            = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tier: Mapped[str]          = mapped_column(SAEnum(CardTier), nullable=False, unique=True)
    price: Mapped[float]       = mapped_column(Float, nullable=False)
    target_members: Mapped[int]= mapped_column(Integer, nullable=False)
    current_members: Mapped[int]= mapped_column(Integer, default=0)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool]    = mapped_column(Boolean, default=True)
    updated_at: Mapped[datetime]= mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

# ── Pydantic ──────────────────────────────────────────────────────────────────

class MemberCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    tier: CardTier
    member_since: Optional[date] = None
    family_size: int = 1
    company_name: Optional[str] = None
    referral_source: Optional[str] = None
    referred_by_id: Optional[str] = None
    notes: Optional[str] = None

class RedemptionCreate(BaseModel):
    member_id: str
    redemption_type: RedemptionType
    value_redeemed: float = 0.0
    notes: Optional[str] = None

class MemberUpdate(BaseModel):
    status: Optional[MemberStatus] = None
    renewal_risk: Optional[RenewalRisk] = None
    visits_ytd: Optional[int] = None
    notes: Optional[str] = None

# ── DB dependency ─────────────────────────────────────────────────────────────

# ── Router ────────────────────────────────────────────────────────────────────

router = APIRouter(prefix="/api/foundation-card", tags=["Foundation Card CRM"])
claude = Anthropic()

FC_CONTEXT = """
You are the AI assistant for the Level Playing Field Foundation Card program.
LPF is a 501(c)(3) nonprofit in Proctor, MN. ED: Shaun Marline.
Mission: Every Kid. Every Sport. Every Opportunity. #TimeToLevelUP
The Foundation Card is a community membership program targeting 1,350 → 4,500 members
generating $416K/yr in revenue. Tiers: Individual $249, Family $399, Corporate $149–$199.
Provide specific, data-driven insights focused on member retention, growth, and revenue pacing.
"""

# ── Seed ──────────────────────────────────────────────────────────────────────

@router.post("/seed", summary="Seed Foundation Card members and tier config")
async def seed_foundation_card(db: AsyncSession = Depends(get_db)) -> dict:
    existing = await db.scalar(select(func.count()).select_from(FoundationCardMember))
    if existing and existing > 0:
        return {"message": f"Already seeded — {existing} members exist", "seeded": False}

    today = date.today()

    # Seed tier config
    tier_configs = [
        CardTierConfig(tier=CardTier.INDIVIDUAL, price=249.0, target_members=2800, description="Individual annual membership"),
        CardTierConfig(tier=CardTier.FAMILY,     price=399.0, target_members=1200, description="Family membership up to 6 members"),
        CardTierConfig(tier=CardTier.CORPORATE,  price=174.0, target_members=400,  description="Corporate sponsor membership"),
        CardTierConfig(tier=CardTier.CHARTER,    price=199.0, target_members=100,  description="Founding/charter members"),
    ]
    for tc in tier_configs:
        db.add(tc)

    # Seed members — mix of tiers, statuses, engagement levels
    members_data = [
        # Active, healthy members
        {"first_name": "David",    "last_name": "Kowalski", "email": "d.kowalski@email.com",  "tier": CardTier.FAMILY,      "status": MemberStatus.ACTIVE,   "member_since": today - timedelta(days=420), "visits_ytd": 48, "redemptions_ytd": 9,  "referral_source": "NXS tournament"},
        {"first_name": "Maria",    "last_name": "Sanchez",  "email": "m.sanchez@email.com",   "tier": CardTier.INDIVIDUAL,  "status": MemberStatus.ACTIVE,   "member_since": today - timedelta(days=310), "visits_ytd": 32, "redemptions_ytd": 7,  "referral_source": "Social media"},
        {"first_name": "Jake",     "last_name": "Nilsson",  "email": "j.nilsson@email.com",   "tier": CardTier.CHARTER,     "status": MemberStatus.ACTIVE,   "member_since": today - timedelta(days=800), "visits_ytd": 60, "redemptions_ytd": 12, "referral_source": "Founding member"},
        {"first_name": "Essentia", "last_name": "Health",   "email": "essentiacard@eh.com",   "tier": CardTier.CORPORATE,   "status": MemberStatus.ACTIVE,   "member_since": today - timedelta(days=180), "visits_ytd": 20, "redemptions_ytd": 5,  "company_name": "Essentia Health"},
        {"first_name": "Angela",   "last_name": "Torres",   "email": "a.torres@email.com",    "tier": CardTier.FAMILY,      "status": MemberStatus.ACTIVE,   "member_since": today - timedelta(days=240), "visits_ytd": 42, "redemptions_ytd": 8,  "family_size": 4, "referral_source": "Rec league"},
        {"first_name": "Brian",    "last_name": "Gustafson","email": "b.gustafson@email.com", "tier": CardTier.INDIVIDUAL,  "status": MemberStatus.ACTIVE,   "member_since": today - timedelta(days=95),  "visits_ytd": 18, "redemptions_ytd": 3},
        # At-risk members
        {"first_name": "Carla",    "last_name": "West",     "email": "c.west@email.com",      "tier": CardTier.INDIVIDUAL,  "status": MemberStatus.ACTIVE,   "member_since": today - timedelta(days=330), "visits_ytd": 4,  "redemptions_ytd": 1,  "renewal_risk": RenewalRisk.HIGH},
        {"first_name": "Tom",      "last_name": "Magnusson","email": "t.magnusson@email.com", "tier": CardTier.FAMILY,      "status": MemberStatus.ACTIVE,   "member_since": today - timedelta(days=350), "visits_ytd": 8,  "redemptions_ytd": 2,  "renewal_risk": RenewalRisk.CRITICAL, "family_size": 3},
        # Expiring soon
        {"first_name": "Priya",    "last_name": "Kumar",    "email": "p.kumar@email.com",     "tier": CardTier.INDIVIDUAL,  "status": MemberStatus.ACTIVE,   "member_since": today - timedelta(days=305), "visits_ytd": 22, "redemptions_ytd": 5},
        {"first_name": "Lakeview", "last_name": "Coffee Co","email": "lakeview@coffee.com",   "tier": CardTier.CORPORATE,   "status": MemberStatus.ACTIVE,   "member_since": today - timedelta(days=340), "visits_ytd": 10, "redemptions_ytd": 3,  "company_name": "Lakeview Coffee"},
        # Expired/cancelled
        {"first_name": "Rachel",   "last_name": "Oberg",    "email": "r.oberg@email.com",     "tier": CardTier.INDIVIDUAL,  "status": MemberStatus.EXPIRED,  "member_since": today - timedelta(days=400), "visits_ytd": 0,  "redemptions_ytd": 0},
        {"first_name": "Fleet",    "last_name": "Farm Duluth","email": "ff.card@fleet.com",   "tier": CardTier.CORPORATE,   "status": MemberStatus.CANCELLED,"member_since": today - timedelta(days=500), "visits_ytd": 0,  "redemptions_ytd": 0,  "company_name": "Fleet Farm Duluth"},
        # New/trial
        {"first_name": "Amara",    "last_name": "Diallo",   "email": "a.diallo@email.com",    "tier": CardTier.INDIVIDUAL,  "status": MemberStatus.TRIAL,    "member_since": today - timedelta(days=10),  "visits_ytd": 3,  "redemptions_ytd": 1},
        {"first_name": "Connor",   "last_name": "Lindberg", "email": "c.lindberg@email.com",  "tier": CardTier.FAMILY,      "status": MemberStatus.PENDING,  "member_since": today,                       "visits_ytd": 0,  "redemptions_ytd": 0,  "family_size": 5},
    ]

    created = []
    for m_data in members_data:
        tier = m_data.get("tier")
        ms = m_data.get("member_since", today - timedelta(days=180))
        risk = m_data.pop("renewal_risk", RenewalRisk.LOW)
        member = FoundationCardMember(
            **m_data,
            annual_fee=TIER_PRICING[tier],
            expiry_date=ms + timedelta(days=365),
            renewal_risk=risk,
            last_activity_date=today - timedelta(days=max(0, 365 - m_data.get("visits_ytd", 1) * 7)),
        )
        db.add(member)
        created.append(member)

    await db.flush()

    # Seed redemptions for active members
    redemption_seeds = [
        (0, RedemptionType.EQUIPMENT_DISCOUNT,   15.0),
        (0, RedemptionType.GUEST_PASS,           0.0),
        (1, RedemptionType.COURT_CREDIT,         20.0),
        (1, RedemptionType.RETAIL_DISCOUNT,      12.0),
        (2, RedemptionType.PRIORITY_BOOKING,     0.0),
        (2, RedemptionType.CAMP_DISCOUNT,        50.0),
        (4, RedemptionType.EQUIPMENT_DISCOUNT,   18.0),
        (5, RedemptionType.COURT_CREDIT,         15.0),
        (8, RedemptionType.RETAIL_DISCOUNT,      8.0),
    ]

    for member_idx, rtype, value in redemption_seeds:
        if member_idx < len(created):
            r = CardRedemption(
                member_id=created[member_idx].id,
                redemption_type=rtype,
                value_redeemed=value,
                redemption_date=today - timedelta(days=14),
            )
            db.add(r)

    await db.commit()
    return {
        "message": "Foundation Card CRM seeded",
        "members": len(members_data),
        "tier_configs": len(tier_configs),
        "redemptions": len(redemption_seeds),
        "seeded": True,
    }

# ── Members ───────────────────────────────────────────────────────────────────

@router.get("/members", summary="List members with filters")
async def list_members(
    tier: Optional[CardTier] = Query(None),
    status: Optional[MemberStatus] = Query(None),
    renewal_risk: Optional[RenewalRisk] = Query(None),
    expiring_soon: bool = Query(False),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    q = select(FoundationCardMember)
    if tier:         q = q.where(FoundationCardMember.tier == tier)
    if status:       q = q.where(FoundationCardMember.status == status)
    if renewal_risk: q = q.where(FoundationCardMember.renewal_risk == renewal_risk)

    result = await db.execute(q)
    members = result.scalars().unique().all()

    if expiring_soon:
        members = [m for m in members if m.is_expiring_soon]

    return [
        {
            "id": m.id,
            "full_name": m.full_name,
            "email": m.email,
            "tier": m.tier,
            "status": m.status,
            "annual_fee": m.annual_fee,
            "member_since": m.member_since.isoformat(),
            "expiry_date": m.expiry_date.isoformat(),
            "days_until_expiry": m.days_until_expiry,
            "is_expiring_soon": m.is_expiring_soon,
            "renewal_risk": m.renewal_risk,
            "engagement_score": m.engagement_score,
            "visits_ytd": m.visits_ytd,
            "redemptions_ytd": m.redemptions_ytd,
            "company_name": m.company_name,
            "family_size": m.family_size,
        }
        for m in members
    ]

@router.post("/enroll", summary="Enroll a new Foundation Card member")
async def enroll_member(payload: MemberCreate, db: AsyncSession = Depends(get_db)) -> dict:
    today = date.today()
    ms = payload.member_since or today
    member = FoundationCardMember(
        **payload.model_dump(exclude={"member_since"}),
        member_since=ms,
        annual_fee=TIER_PRICING[payload.tier],
        expiry_date=ms + timedelta(days=365),
    )
    db.add(member)
    await db.commit()
    await db.refresh(member)
    return {"id": member.id, "full_name": member.full_name, "annual_fee": member.annual_fee, "message": "Member enrolled"}

@router.patch("/members/{member_id}", summary="Update member status or risk")
async def update_member(member_id: str, payload: MemberUpdate, db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(select(FoundationCardMember).where(FoundationCardMember.id == member_id))
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(404, "Member not found")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(member, k, v)
    await db.commit()
    return {"id": member.id, "message": "Member updated"}

@router.post("/redeem", summary="Record a benefit redemption")
async def record_redemption(payload: RedemptionCreate, db: AsyncSession = Depends(get_db)) -> dict:
    r = CardRedemption(**payload.model_dump())
    db.add(r)
    # Increment member's redemption count
    result = await db.execute(select(FoundationCardMember).where(FoundationCardMember.id == payload.member_id))
    member = result.scalar_one_or_none()
    if member:
        member.redemptions_ytd += 1
        member.last_activity_date = date.today()
    await db.commit()
    return {"message": "Redemption recorded"}

# ── KPIs + Revenue ────────────────────────────────────────────────────────────

@router.get("/kpis", summary="Foundation Card KPI snapshot")
async def card_kpis(db: AsyncSession = Depends(get_db)) -> dict:
    active_q = await db.execute(select(func.count()).select_from(FoundationCardMember).where(FoundationCardMember.status == MemberStatus.ACTIVE))
    active = active_q.scalar() or 0

    rev_q = await db.execute(select(func.sum(FoundationCardMember.annual_fee)).where(FoundationCardMember.status == MemberStatus.ACTIVE))
    annual_revenue = rev_q.scalar() or 0.0

    target_revenue = 416_000.0
    target_members = 4_500

    at_risk_q = await db.execute(select(func.count()).select_from(FoundationCardMember).where(
        FoundationCardMember.renewal_risk.in_([RenewalRisk.HIGH, RenewalRisk.CRITICAL]),
        FoundationCardMember.status == MemberStatus.ACTIVE
    ))
    at_risk = at_risk_q.scalar() or 0

    expiring_q = await db.execute(select(FoundationCardMember).where(FoundationCardMember.status == MemberStatus.ACTIVE))
    all_active = expiring_q.scalars().all()
    expiring_60d = sum(1 for m in all_active if m.is_expiring_soon)
    avg_engagement = round(sum(m.engagement_score for m in all_active) / len(all_active), 1) if all_active else 0

    tier_q = await db.execute(select(FoundationCardMember.tier, func.count(), func.sum(FoundationCardMember.annual_fee))
                               .where(FoundationCardMember.status == MemberStatus.ACTIVE)
                               .group_by(FoundationCardMember.tier))
    tier_breakdown = {row[0]: {"members": row[1], "revenue": round(row[2] or 0, 2)} for row in tier_q.all()}

    redemptions_q = await db.execute(select(func.sum(CardRedemption.value_redeemed)))
    total_value_redeemed = redemptions_q.scalar() or 0.0

    return {
        "active_members": active,
        "target_members": target_members,
        "member_pacing_pct": round(active / target_members * 100, 1),
        "annual_revenue": round(annual_revenue, 2),
        "target_revenue": target_revenue,
        "revenue_pacing_pct": round(annual_revenue / target_revenue * 100, 1),
        "monthly_revenue": round(annual_revenue / 12, 2),
        "at_risk_members": at_risk,
        "expiring_60d": expiring_60d,
        "avg_engagement_score": avg_engagement,
        "total_value_redeemed": round(total_value_redeemed, 2),
        "tier_breakdown": tier_breakdown,
    }

@router.get("/revenue-pacing", summary="Monthly revenue pacing vs $416K/yr target")
async def revenue_pacing(db: AsyncSession = Depends(get_db)) -> dict:
    kpis = await card_kpis(db)
    monthly_target = 416_000 / 12
    return {
        "monthly_actual": kpis["monthly_revenue"],
        "monthly_target": round(monthly_target, 2),
        "monthly_gap": round(monthly_target - kpis["monthly_revenue"], 2),
        "annual_actual": kpis["annual_revenue"],
        "annual_target": kpis["target_revenue"],
        "annual_gap": round(kpis["target_revenue"] - kpis["annual_revenue"], 2),
        "members_to_target": kpis["target_members"] - kpis["active_members"],
        "revenue_pacing_pct": kpis["revenue_pacing_pct"],
        "member_pacing_pct": kpis["member_pacing_pct"],
        "projection_to_hit_target": _calc_needed_members(kpis),
    }

def _calc_needed_members(kpis: dict) -> dict:
    gap = kpis["target_revenue"] - kpis["annual_revenue"]
    avg_fee = kpis["annual_revenue"] / kpis["active_members"] if kpis["active_members"] else 249.0
    return {
        "revenue_gap": round(gap, 2),
        "avg_annual_fee": round(avg_fee, 2),
        "new_members_needed": max(0, round(gap / avg_fee)),
    }

# ── Renewal Risk ──────────────────────────────────────────────────────────────

@router.post("/ai-renewal-risk", summary="AI renewal risk assessment and win-back recommendations")
async def ai_renewal_risk(db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(select(FoundationCardMember).where(
        FoundationCardMember.status == MemberStatus.ACTIVE,
        FoundationCardMember.renewal_risk.in_([RenewalRisk.HIGH, RenewalRisk.CRITICAL])
    ))
    at_risk = result.scalars().all()

    kpis = await card_kpis(db)

    at_risk_data = "\n".join(
        f"- {m.full_name} ({m.tier}): {m.days_until_expiry}d until expiry, "
        f"engagement {m.engagement_score}/100, visits {m.visits_ytd}, "
        f"redemptions {m.redemptions_ytd}, risk={m.renewal_risk}"
        for m in at_risk[:10]
    )

    prompt = f"""
Foundation Card Program — Renewal Risk Analysis

Program KPIs:
- Active members: {kpis['active_members']} / {kpis['target_members']} target ({kpis['member_pacing_pct']}%)
- Annual revenue: ${kpis['annual_revenue']:,.0f} / $416,000 target ({kpis['revenue_pacing_pct']}%)
- Members expiring in 60 days: {kpis['expiring_60d']}
- At-risk members: {kpis['at_risk_members']}
- Avg engagement score: {kpis['avg_engagement_score']}/100

At-risk member profiles:
{at_risk_data}

Generate a 3-paragraph renewal strategy brief:
1. Assess overall renewal risk exposure in revenue terms and identify the most critical win-back targets
2. Recommend specific outreach tactics for CRITICAL vs HIGH risk members — what to say, what to offer, what channel to use
3. Structural recommendations to improve retention — which benefits are underused, what engagement triggers are missing, and what would close the ${'${:,.0f}'.format(kpis['target_revenue'] - kpis['annual_revenue'])} revenue gap fastest
"""

    response = claude.messages.create(
        model="claude-opus-4-5",
        max_tokens=650,
        system=FC_CONTEXT,
        messages=[{"role": "user", "content": prompt}],
    )

    return {
        "brief": response.content[0].text,
        "at_risk_members": [
            {"id": m.id, "full_name": m.full_name, "tier": m.tier, "risk": m.renewal_risk,
             "days_until_expiry": m.days_until_expiry, "engagement_score": m.engagement_score,
             "annual_fee": m.annual_fee}
            for m in at_risk
        ],
        "revenue_at_risk": round(sum(m.annual_fee for m in at_risk), 2),
        "generated_at": datetime.utcnow().isoformat(),
    }

@router.post("/ai-growth-brief", summary="AI member growth and pipeline strategy")
async def ai_growth_brief(db: AsyncSession = Depends(get_db)) -> dict:
    kpis = await card_kpis(db)
    pacing = await revenue_pacing(db)

    prompt = f"""
Foundation Card Program — Growth Strategy

Current state:
- Active members: {kpis['active_members']} (target: {kpis['target_members']}, gap: {pacing['members_to_target']})
- Monthly revenue: ${kpis['monthly_revenue']:,.0f} (target: ${pacing['monthly_target']:,.0f}, gap: ${pacing['monthly_gap']:,.0f}/mo)
- Tier mix: {kpis['tier_breakdown']}
- Avg engagement: {kpis['avg_engagement_score']}/100
- New members needed to hit revenue target: {pacing['projection_to_hit_target']['new_members_needed']}

The Foundation Card program supports LPF's mission: Every Kid. Every Sport. Every Opportunity.
NXS National Complex hosts 40+ tournaments/year, leagues, camps, and community programs at 704 Kirkus St, Proctor MN.

Generate a 3-paragraph growth strategy:
1. Fastest path to close the member gap — which tier to push hardest and why
2. Specific acquisition channels and tactics using NXS's existing tournament traffic, LPF programs, and local employer base
3. Partnership and corporate membership play — how to use the Corporate tier to recruit Essentia Health, local businesses, and regional employers as Foundation Card sponsors
"""

    response = claude.messages.create(
        model="claude-opus-4-5",
        max_tokens=650,
        system=FC_CONTEXT,
        messages=[{"role": "user", "content": prompt}],
    )

    return {
        "brief": response.content[0].text,
        "pacing_snapshot": pacing,
        "generated_at": datetime.utcnow().isoformat(),
    }

@router.get("/tier-benefits", summary="Return benefit list for all tiers")
async def tier_benefits() -> dict:
    return {
        tier.value: {
            "price": TIER_PRICING[tier],
            "benefits": TIER_BENEFITS[tier],
        }
        for tier in CardTier
    }
