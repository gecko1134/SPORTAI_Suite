"""
SportAI Suite — NIL Program AI Router
Sprint 1 · Level Playing Field Foundation
50+ HS athlete contracts, brand deal logging, compliance tracking, AI briefs

Add to main.py:
    from routers.nil_ai import router as nil_router
    app.include_router(nil_router)
"""

from __future__ import annotations

import enum
import uuid
from datetime import date, datetime, timedelta
from typing import Any, Optional

from anthropic import Anthropic
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import (
    Boolean, Column, Date, DateTime, Enum as SAEnum,
    Float, ForeignKey, Integer, String, Text, func, select
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# ── Shared Base (import from your models.domain if preferred) ─────────────────
class Base(DeclarativeBase):
    pass


# ── Enums ─────────────────────────────────────────────────────────────────────

class Sport(str, enum.Enum):
    FLAG_FOOTBALL = "flag_football"
    SOCCER        = "soccer"
    LACROSSE      = "lacrosse"
    VOLLEYBALL    = "volleyball"
    SOFTBALL      = "softball"
    BASKETBALL    = "basketball"
    PICKLEBALL    = "pickleball"
    ROBOTICS      = "robotics"
    MULTI_SPORT   = "multi_sport"
    OTHER         = "other"


class DealStatus(str, enum.Enum):
    ACTIVE    = "active"
    PENDING   = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED   = "expired"


class DealType(str, enum.Enum):
    SOCIAL_MEDIA      = "social_media"
    APPEARANCE        = "appearance"
    EQUIPMENT         = "equipment"
    CAMP_PROMOTION    = "camp_promotion"
    COMMUNITY_SERVICE = "community_service"
    AMBASSADOR        = "ambassador"
    CONTENT_CREATION  = "content_creation"
    OTHER             = "other"


class ComplianceStatus(str, enum.Enum):
    COMPLIANT       = "compliant"
    PENDING_REVIEW  = "pending_review"
    WARNING         = "warning"
    VIOLATION       = "violation"


class GradeLevel(str, enum.Enum):
    FRESHMAN  = "9th"
    SOPHOMORE = "10th"
    JUNIOR    = "11th"
    SENIOR    = "12th"


# ── ORM Models ────────────────────────────────────────────────────────────────

class NILAthlete(Base):
    """HS athlete enrolled in the LPF NIL Program."""
    __tablename__ = "nil_athletes"

    id: Mapped[str]            = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name: Mapped[str]    = mapped_column(String(100), nullable=False)
    last_name: Mapped[str]     = mapped_column(String(100), nullable=False)
    email: Mapped[str]         = mapped_column(String(255), nullable=True)
    phone: Mapped[str]         = mapped_column(String(20), nullable=True)
    school: Mapped[str]        = mapped_column(String(200), nullable=False)
    grade: Mapped[str]         = mapped_column(SAEnum(GradeLevel), nullable=False)
    sport_primary: Mapped[str] = mapped_column(SAEnum(Sport), nullable=False)
    sport_secondary: Mapped[Optional[str]] = mapped_column(SAEnum(Sport), nullable=True)
    gpa: Mapped[Optional[float]]           = mapped_column(Float, nullable=True)
    social_followers: Mapped[int]          = mapped_column(Integer, default=0)
    bio: Mapped[Optional[str]]             = mapped_column(Text, nullable=True)
    is_active: Mapped[bool]                = mapped_column(Boolean, default=True)
    enrolled_at: Mapped[datetime]          = mapped_column(DateTime(timezone=True), server_default=func.now())
    graduation_date: Mapped[Optional[date]]= mapped_column(Date, nullable=True)
    compliance_status: Mapped[str]         = mapped_column(SAEnum(ComplianceStatus), default=ComplianceStatus.COMPLIANT)
    created_at: Mapped[datetime]           = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime]           = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    deals: Mapped[list["NILDeal"]]                     = relationship("NILDeal", back_populates="athlete", cascade="all, delete-orphan")
    compliance_events: Mapped[list["NILComplianceEvent"]] = relationship("NILComplianceEvent", back_populates="athlete", cascade="all, delete-orphan")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def total_deal_value(self) -> float:
        return sum(d.deal_value for d in self.deals if d.status == DealStatus.ACTIVE)

    @property
    def active_deals(self) -> int:
        return sum(1 for d in self.deals if d.status == DealStatus.ACTIVE)


class NILDeal(Base):
    """Brand deal or partnership for an NIL athlete."""
    __tablename__ = "nil_deals"

    id: Mapped[str]              = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    athlete_id: Mapped[str]      = mapped_column(ForeignKey("nil_athletes.id"), nullable=False)
    brand_name: Mapped[str]      = mapped_column(String(200), nullable=False)
    deal_type: Mapped[str]       = mapped_column(SAEnum(DealType), nullable=False)
    deal_value: Mapped[float]    = mapped_column(Float, nullable=False, default=0.0)
    status: Mapped[str]          = mapped_column(SAEnum(DealStatus), default=DealStatus.ACTIVE)
    start_date: Mapped[date]     = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[date]]       = mapped_column(Date, nullable=True)
    deliverables: Mapped[Optional[str]]    = mapped_column(Text, nullable=True)
    social_posts_required: Mapped[int]     = mapped_column(Integer, default=0)
    social_posts_completed: Mapped[int]    = mapped_column(Integer, default=0)
    appearances_required: Mapped[int]      = mapped_column(Integer, default=0)
    appearances_completed: Mapped[int]     = mapped_column(Integer, default=0)
    notes: Mapped[Optional[str]]           = mapped_column(Text, nullable=True)
    contract_url: Mapped[Optional[str]]    = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime]           = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime]           = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    athlete: Mapped["NILAthlete"] = relationship("NILAthlete", back_populates="deals")

    @property
    def completion_pct(self) -> float:
        total = self.social_posts_required + self.appearances_required
        done = self.social_posts_completed + self.appearances_completed
        return round((done / total * 100) if total > 0 else 0, 1)

    @property
    def is_expiring_soon(self) -> bool:
        if not self.end_date:
            return False
        return self.end_date <= date.today() + timedelta(days=30)


class NILComplianceEvent(Base):
    """Compliance audit log — tracks state rule adherence for each athlete."""
    __tablename__ = "nil_compliance_events"

    id: Mapped[str]              = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    athlete_id: Mapped[str]      = mapped_column(ForeignKey("nil_athletes.id"), nullable=False)
    event_type: Mapped[str]      = mapped_column(String(100), nullable=False)  # e.g. "annual_disclosure", "deal_review"
    status: Mapped[str]          = mapped_column(SAEnum(ComplianceStatus), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    due_date: Mapped[Optional[date]]      = mapped_column(Date, nullable=True)
    resolved_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime]          = mapped_column(DateTime(timezone=True), server_default=func.now())

    athlete: Mapped["NILAthlete"] = relationship("NILAthlete", back_populates="compliance_events")


# ── Pydantic Schemas ──────────────────────────────────────────────────────────

class AthleteCreate(BaseModel):
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    school: str
    grade: GradeLevel
    sport_primary: Sport
    sport_secondary: Optional[Sport] = None
    gpa: Optional[float] = None
    social_followers: int = 0
    bio: Optional[str] = None
    graduation_date: Optional[date] = None


class DealCreate(BaseModel):
    athlete_id: str
    brand_name: str
    deal_type: DealType
    deal_value: float
    start_date: date
    end_date: Optional[date] = None
    deliverables: Optional[str] = None
    social_posts_required: int = 0
    appearances_required: int = 0
    notes: Optional[str] = None
    contract_url: Optional[str] = None


class DealUpdate(BaseModel):
    status: Optional[DealStatus] = None
    social_posts_completed: Optional[int] = None
    appearances_completed: Optional[int] = None
    notes: Optional[str] = None
    end_date: Optional[date] = None


class ComplianceEventCreate(BaseModel):
    athlete_id: str
    event_type: str
    status: ComplianceStatus
    notes: Optional[str] = None
    due_date: Optional[date] = None


# ── Database dependency (replace with your get_db) ────────────────────────────

async def get_db() -> AsyncSession:  # pragma: no cover
    raise NotImplementedError("Wire to your AsyncSession factory")


# ── Router ────────────────────────────────────────────────────────────────────

router = APIRouter(prefix="/api/nil", tags=["NIL Program"])
claude = Anthropic()

NIL_CONTEXT = """
You are the AI assistant for the Level Playing Field Foundation's NIL (Name, Image, Likeness) Program.
LPF is a 501(c)(3) nonprofit based in Proctor, MN. Mission: "Every Kid. Every Sport. Every Opportunity."
The NIL Program supports 50+ high school athletes across 8 sports:
flag football, soccer, lacrosse, volleyball, softball, basketball, pickleball, robotics.
NXS National Complex is at 704 Kirkus Street, Proctor MN. ED: Shaun Marline.
Respond with specific, actionable insights. Keep briefs to 3 clear paragraphs.
"""


# ── Seed ──────────────────────────────────────────────────────────────────────

@router.post("/seed", summary="Seed 12 sample NIL athletes with deals")
async def seed_nil(db: AsyncSession = Depends(get_db)) -> dict:
    existing = await db.scalar(select(func.count()).select_from(NILAthlete))
    if existing and existing > 0:
        return {"message": f"Already seeded — {existing} athletes exist", "seeded": False}

    athletes_data = [
        {"first_name": "Marcus",   "last_name": "Johnson",  "school": "Duluth East HS",     "grade": GradeLevel.SENIOR,    "sport_primary": Sport.BASKETBALL,     "social_followers": 4200, "gpa": 3.7},
        {"first_name": "Aaliyah",  "last_name": "Rivera",   "school": "Proctor HS",          "grade": GradeLevel.JUNIOR,    "sport_primary": Sport.VOLLEYBALL,     "social_followers": 2800, "gpa": 3.9},
        {"first_name": "Devon",    "last_name": "Kowalski", "school": "Cloquet HS",          "grade": GradeLevel.SENIOR,    "sport_primary": Sport.SOCCER,         "social_followers": 1900, "gpa": 3.4},
        {"first_name": "Sierra",   "last_name": "Thompson", "school": "Duluth Central HS",   "grade": GradeLevel.SOPHOMORE, "sport_primary": Sport.SOFTBALL,       "social_followers": 3100, "gpa": 3.8},
        {"first_name": "Jordan",   "last_name": "Williams", "school": "Hermantown HS",       "grade": GradeLevel.JUNIOR,    "sport_primary": Sport.FLAG_FOOTBALL,  "social_followers": 5500, "gpa": 3.5},
        {"first_name": "Priya",    "last_name": "Patel",    "school": "Duluth Marshall HS",  "grade": GradeLevel.SENIOR,    "sport_primary": Sport.PICKLEBALL,     "social_followers": 2200, "gpa": 4.0},
        {"first_name": "Elijah",   "last_name": "Carter",   "school": "Esko HS",             "grade": GradeLevel.JUNIOR,    "sport_primary": Sport.LACROSSE,       "social_followers": 1700, "gpa": 3.3},
        {"first_name": "Makena",   "last_name": "Okafor",   "school": "Proctor HS",          "grade": GradeLevel.SENIOR,    "sport_primary": Sport.BASKETBALL,     "social_followers": 6100, "gpa": 3.6},
        {"first_name": "Tyler",    "last_name": "Anderson", "school": "Two Harbors HS",      "grade": GradeLevel.FRESHMAN,  "sport_primary": Sport.SOCCER,         "social_followers": 900,  "gpa": 3.9},
        {"first_name": "Imani",    "last_name": "Brooks",   "school": "Duluth East HS",      "grade": GradeLevel.JUNIOR,    "sport_primary": Sport.VOLLEYBALL,     "social_followers": 3800, "gpa": 3.7},
        {"first_name": "Nathan",   "last_name": "Lindqvist","school": "Duluth Central HS",   "grade": GradeLevel.SENIOR,    "sport_primary": Sport.FLAG_FOOTBALL,  "social_followers": 2100, "gpa": 3.2},
        {"first_name": "Zoe",      "last_name": "Magnusson","school": "Hermantown HS",       "grade": GradeLevel.SOPHOMORE, "sport_primary": Sport.ROBOTICS,       "social_followers": 4700, "gpa": 4.0},
    ]

    created_athletes = []
    for a_data in athletes_data:
        athlete = NILAthlete(**a_data)
        db.add(athlete)
        created_athletes.append(athlete)

    await db.flush()  # get IDs

    deals_data = [
        {"athlete_idx": 0, "brand_name": "Duluth Trading Co",   "deal_type": DealType.AMBASSADOR,        "deal_value": 1200.0, "social_posts_required": 4, "start_date": date(2026, 1, 1), "end_date": date(2026, 6, 30)},
        {"athlete_idx": 1, "brand_name": "Lake Superior Brew",  "deal_type": DealType.SOCIAL_MEDIA,      "deal_value": 750.0,  "social_posts_required": 6, "start_date": date(2026, 2, 1)},
        {"athlete_idx": 2, "brand_name": "North Shore Gear",    "deal_type": DealType.EQUIPMENT,         "deal_value": 500.0,  "start_date": date(2026, 1, 15)},
        {"athlete_idx": 4, "brand_name": "Essentia Health",     "deal_type": DealType.COMMUNITY_SERVICE, "deal_value": 800.0,  "appearances_required": 3, "start_date": date(2026, 3, 1)},
        {"athlete_idx": 5, "brand_name": "NXS National Complex","deal_type": DealType.CAMP_PROMOTION,    "deal_value": 600.0,  "social_posts_required": 3, "start_date": date(2026, 1, 1)},
        {"athlete_idx": 7, "brand_name": "Fleet Farm Duluth",   "deal_type": DealType.AMBASSADOR,        "deal_value": 1500.0, "social_posts_required": 8, "start_date": date(2026, 2, 15), "end_date": date(2026, 8, 15)},
        {"athlete_idx": 9, "brand_name": "Lakeview Coffee",     "deal_type": DealType.CONTENT_CREATION,  "deal_value": 400.0,  "social_posts_required": 5, "start_date": date(2026, 3, 1)},
        {"athlete_idx": 11,"brand_name": "Tech North MN",       "deal_type": DealType.AMBASSADOR,        "deal_value": 950.0,  "social_posts_required": 4, "start_date": date(2026, 1, 1)},
    ]

    for d_data in deals_data:
        idx = d_data.pop("athlete_idx")
        deal = NILDeal(athlete_id=created_athletes[idx].id, status=DealStatus.ACTIVE, **d_data)
        db.add(deal)

    # Seed some compliance events
    for i, athlete in enumerate(created_athletes):
        event = NILComplianceEvent(
            athlete_id=athlete.id,
            event_type="annual_disclosure",
            status=ComplianceStatus.COMPLIANT if i % 4 != 3 else ComplianceStatus.PENDING_REVIEW,
            due_date=date(2026, 6, 30),
            notes="Annual NIL disclosure — MN state requirement",
        )
        db.add(event)

    await db.commit()
    return {
        "message": "NIL Program seeded successfully",
        "athletes": len(athletes_data),
        "deals": len(deals_data),
        "compliance_events": len(athletes_data),
        "seeded": True,
    }


# ── Athletes ──────────────────────────────────────────────────────────────────

@router.get("/athletes", summary="List all NIL athletes with deal summaries")
async def list_athletes(
    sport: Optional[Sport] = Query(None),
    grade: Optional[GradeLevel] = Query(None),
    compliance_status: Optional[ComplianceStatus] = Query(None),
    active_only: bool = Query(True),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    q = select(NILAthlete)
    if sport:
        q = q.where(NILAthlete.sport_primary == sport)
    if grade:
        q = q.where(NILAthlete.grade == grade)
    if compliance_status:
        q = q.where(NILAthlete.compliance_status == compliance_status)
    if active_only:
        q = q.where(NILAthlete.is_active == True)

    result = await db.execute(q)
    athletes = result.scalars().unique().all()

    return [
        {
            "id": a.id,
            "full_name": a.full_name,
            "school": a.school,
            "grade": a.grade,
            "sport_primary": a.sport_primary,
            "gpa": a.gpa,
            "social_followers": a.social_followers,
            "active_deals": a.active_deals,
            "total_deal_value": a.total_deal_value,
            "compliance_status": a.compliance_status,
            "enrolled_at": a.enrolled_at.isoformat(),
        }
        for a in athletes
    ]


@router.post("/athletes", summary="Enroll a new NIL athlete")
async def create_athlete(payload: AthleteCreate, db: AsyncSession = Depends(get_db)) -> dict:
    athlete = NILAthlete(**payload.model_dump())
    db.add(athlete)
    await db.commit()
    await db.refresh(athlete)
    return {"id": athlete.id, "full_name": athlete.full_name, "message": "Athlete enrolled successfully"}


@router.get("/athletes/{athlete_id}", summary="Get athlete detail with all deals")
async def get_athlete(athlete_id: str, db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(select(NILAthlete).where(NILAthlete.id == athlete_id))
    athlete = result.scalar_one_or_none()
    if not athlete:
        raise HTTPException(404, "Athlete not found")

    return {
        "id": athlete.id,
        "full_name": athlete.full_name,
        "email": athlete.email,
        "phone": athlete.phone,
        "school": athlete.school,
        "grade": athlete.grade,
        "sport_primary": athlete.sport_primary,
        "sport_secondary": athlete.sport_secondary,
        "gpa": athlete.gpa,
        "social_followers": athlete.social_followers,
        "bio": athlete.bio,
        "compliance_status": athlete.compliance_status,
        "is_active": athlete.is_active,
        "enrolled_at": athlete.enrolled_at.isoformat(),
        "graduation_date": athlete.graduation_date.isoformat() if athlete.graduation_date else None,
        "deals": [
            {
                "id": d.id,
                "brand_name": d.brand_name,
                "deal_type": d.deal_type,
                "deal_value": d.deal_value,
                "status": d.status,
                "start_date": d.start_date.isoformat(),
                "end_date": d.end_date.isoformat() if d.end_date else None,
                "completion_pct": d.completion_pct,
                "is_expiring_soon": d.is_expiring_soon,
                "social_posts_required": d.social_posts_required,
                "social_posts_completed": d.social_posts_completed,
                "appearances_required": d.appearances_required,
                "appearances_completed": d.appearances_completed,
            }
            for d in athlete.deals
        ],
        "compliance_events": [
            {
                "id": e.id,
                "event_type": e.event_type,
                "status": e.status,
                "due_date": e.due_date.isoformat() if e.due_date else None,
                "resolved_date": e.resolved_date.isoformat() if e.resolved_date else None,
                "notes": e.notes,
            }
            for e in athlete.compliance_events
        ],
    }


# ── Deals ─────────────────────────────────────────────────────────────────────

@router.get("/deals", summary="List all deals with optional filters")
async def list_deals(
    status: Optional[DealStatus] = Query(None),
    deal_type: Optional[DealType] = Query(None),
    expiring_soon: bool = Query(False),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    q = select(NILDeal)
    if status:
        q = q.where(NILDeal.status == status)
    if deal_type:
        q = q.where(NILDeal.deal_type == deal_type)

    result = await db.execute(q)
    deals = result.scalars().all()

    if expiring_soon:
        deals = [d for d in deals if d.is_expiring_soon]

    return [
        {
            "id": d.id,
            "athlete_id": d.athlete_id,
            "brand_name": d.brand_name,
            "deal_type": d.deal_type,
            "deal_value": d.deal_value,
            "status": d.status,
            "start_date": d.start_date.isoformat(),
            "end_date": d.end_date.isoformat() if d.end_date else None,
            "completion_pct": d.completion_pct,
            "is_expiring_soon": d.is_expiring_soon,
        }
        for d in deals
    ]


@router.post("/deals", summary="Log a new brand deal")
async def create_deal(payload: DealCreate, db: AsyncSession = Depends(get_db)) -> dict:
    deal = NILDeal(**payload.model_dump())
    db.add(deal)
    await db.commit()
    await db.refresh(deal)
    return {"id": deal.id, "message": "Deal logged successfully"}


@router.patch("/deals/{deal_id}", summary="Update deal progress or status")
async def update_deal(deal_id: str, payload: DealUpdate, db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(select(NILDeal).where(NILDeal.id == deal_id))
    deal = result.scalar_one_or_none()
    if not deal:
        raise HTTPException(404, "Deal not found")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(deal, k, v)
    await db.commit()
    return {"id": deal.id, "message": "Deal updated"}


# ── Compliance ────────────────────────────────────────────────────────────────

@router.get("/compliance-alerts", summary="All open compliance issues and upcoming deadlines")
async def compliance_alerts(db: AsyncSession = Depends(get_db)) -> dict:
    q = select(NILComplianceEvent).where(
        NILComplianceEvent.status.in_([ComplianceStatus.PENDING_REVIEW, ComplianceStatus.WARNING, ComplianceStatus.VIOLATION])
    )
    result = await db.execute(q)
    open_events = result.scalars().all()

    # Upcoming deadlines (due within 60 days)
    deadline_cutoff = date.today() + timedelta(days=60)
    dq = select(NILComplianceEvent).where(
        NILComplianceEvent.due_date <= deadline_cutoff,
        NILComplianceEvent.resolved_date == None,
        NILComplianceEvent.status != ComplianceStatus.VIOLATION,
    )
    dq_result = await db.execute(dq)
    upcoming = dq_result.scalars().all()

    return {
        "open_issues": [
            {"id": e.id, "athlete_id": e.athlete_id, "event_type": e.event_type, "status": e.status, "due_date": e.due_date.isoformat() if e.due_date else None, "notes": e.notes}
            for e in open_events
        ],
        "upcoming_deadlines": [
            {"id": e.id, "athlete_id": e.athlete_id, "event_type": e.event_type, "due_date": e.due_date.isoformat(), "days_until_due": (e.due_date - date.today()).days}
            for e in upcoming if e.due_date
        ],
        "summary": {
            "open_count": len(open_events),
            "upcoming_deadline_count": len(upcoming),
        }
    }


@router.post("/compliance", summary="Log a compliance event")
async def log_compliance(payload: ComplianceEventCreate, db: AsyncSession = Depends(get_db)) -> dict:
    event = NILComplianceEvent(**payload.model_dump())
    db.add(event)
    await db.commit()
    return {"message": "Compliance event logged"}


# ── Program KPIs ──────────────────────────────────────────────────────────────

@router.get("/kpis", summary="Program-level KPI snapshot")
async def nil_kpis(db: AsyncSession = Depends(get_db)) -> dict:
    athlete_count = await db.scalar(select(func.count()).select_from(NILAthlete).where(NILAthlete.is_active == True))
    deal_count    = await db.scalar(select(func.count()).select_from(NILDeal).where(NILDeal.status == DealStatus.ACTIVE))
    total_value   = await db.scalar(select(func.sum(NILDeal.deal_value)).where(NILDeal.status == DealStatus.ACTIVE)) or 0.0
    violations    = await db.scalar(select(func.count()).select_from(NILComplianceEvent).where(NILComplianceEvent.status == ComplianceStatus.VIOLATION)) or 0

    avg_followers_result = await db.execute(select(func.avg(NILAthlete.social_followers)).where(NILAthlete.is_active == True))
    avg_followers = round(avg_followers_result.scalar() or 0)

    expiring_q = await db.execute(select(NILDeal).where(NILDeal.status == DealStatus.ACTIVE))
    expiring = sum(1 for d in expiring_q.scalars().all() if d.is_expiring_soon)

    sports_q = await db.execute(select(NILAthlete.sport_primary, func.count()).group_by(NILAthlete.sport_primary))
    sports_breakdown = {row[0]: row[1] for row in sports_q.all()}

    return {
        "active_athletes": athlete_count,
        "active_deals": deal_count,
        "total_deal_value": round(total_value, 2),
        "avg_deal_per_athlete": round(total_value / athlete_count, 2) if athlete_count else 0,
        "avg_social_followers": avg_followers,
        "compliance_violations": violations,
        "deals_expiring_soon": expiring,
        "sports_breakdown": sports_breakdown,
    }


# ── AI Brief ──────────────────────────────────────────────────────────────────

@router.post("/ai-brief/{athlete_id}", summary="Generate AI athlete brief with deal strategy")
async def athlete_ai_brief(athlete_id: str, db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(select(NILAthlete).where(NILAthlete.id == athlete_id))
    athlete = result.scalar_one_or_none()
    if not athlete:
        raise HTTPException(404, "Athlete not found")

    deals_summary = "\n".join(
        f"- {d.brand_name} ({d.deal_type}) ${d.deal_value:.0f} — {d.completion_pct}% complete, expires {d.end_date or 'ongoing'}"
        for d in athlete.deals
    ) or "No active deals"

    prompt = f"""
Athlete profile:
- Name: {athlete.full_name}
- School: {athlete.school}, Grade: {athlete.grade}
- Sport: {athlete.sport_primary}
- GPA: {athlete.gpa or 'N/A'}
- Social followers: {athlete.social_followers:,}
- Compliance status: {athlete.compliance_status}
- Active deals ({athlete.active_deals}):
{deals_summary}

Generate a 3-paragraph NIL Program brief covering:
1. Athlete status, strengths, and current deal performance
2. Compliance standing and any action items needed
3. Recommended next steps — new brand categories to pursue, deal types that fit this athlete's profile, and specific NXS/LPF promotional opportunities they should be activated for
"""

    response = claude.messages.create(
        model="claude-opus-4-5",
        max_tokens=600,
        system=NIL_CONTEXT,
        messages=[{"role": "user", "content": prompt}],
    )

    return {
        "athlete_id": athlete_id,
        "athlete_name": athlete.full_name,
        "brief": response.content[0].text,
        "generated_at": datetime.utcnow().isoformat(),
    }


@router.post("/ai-program-brief", summary="Generate program-level NIL strategy brief")
async def program_ai_brief(db: AsyncSession = Depends(get_db)) -> dict:
    kpis = await nil_kpis(db)
    alerts = await compliance_alerts(db)

    prompt = f"""
LPF NIL Program current state:
- Active athletes: {kpis['active_athletes']}
- Active brand deals: {kpis['active_deals']}
- Total deal value: ${kpis['total_deal_value']:,.0f}
- Avg deal per athlete: ${kpis['avg_deal_per_athlete']:,.0f}
- Avg social followers: {kpis['avg_social_followers']:,}
- Sports represented: {kpis['sports_breakdown']}
- Compliance violations: {kpis['compliance_violations']}
- Deals expiring in 30 days: {kpis['deals_expiring_soon']}
- Open compliance issues: {alerts['summary']['open_count']}

Generate a 3-paragraph executive program brief covering:
1. Overall program health and deal portfolio performance
2. Compliance standing and immediate action items
3. Strategic recommendations — which sports/athlete profiles to recruit next, which brand categories are underrepresented, and how to leverage NXS/LPF events for NIL activation
"""

    response = claude.messages.create(
        model="claude-opus-4-5",
        max_tokens=600,
        system=NIL_CONTEXT,
        messages=[{"role": "user", "content": prompt}],
    )

    return {
        "brief": response.content[0].text,
        "kpis_snapshot": kpis,
        "generated_at": datetime.utcnow().isoformat(),
    }
