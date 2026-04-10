"""
SportAI Suite — Membership Value Predictor
Sprint 8 · Nexus Domes Inc.
Churn prediction (30/60/90-day windows) · LTV scoring · Engagement decay detection
Automated win-back sequences · Tier upgrade propensity modeling
Explorer, Active, and premium member tiers

Add to main.py:
    from routers.membership_predictor import router as membership_predictor_router
    app.include_router(membership_predictor_router)
"""

from __future__ import annotations

import enum
import math
import uuid
from datetime import date, datetime, timedelta
from typing import Optional
import random

from anthropic import Anthropic
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import (
    Boolean, Date, DateTime, Enum as SAEnum, Float,
    ForeignKey, Integer, String, Text, func, select
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# ── Enums ─────────────────────────────────────────────────────────────────────

class MemberTier(str, enum.Enum):
    EXPLORER   = "explorer"     # Entry-level
    ACTIVE     = "active"       # Standard
    ELITE      = "elite"        # Premium
    CHARTER    = "charter"      # Founding/legacy
    CORPORATE  = "corporate"    # Business accounts


class ChurnRiskBand(str, enum.Enum):
    SAFE     = "safe"        # <10% churn probability
    WATCH    = "watch"       # 10–25%
    AT_RISK  = "at_risk"     # 25–50%
    CRITICAL = "critical"    # >50%


class WinBackStatus(str, enum.Enum):
    PENDING   = "pending"
    SENT      = "sent"
    OPENED    = "opened"
    CONVERTED = "converted"
    EXPIRED   = "expired"


class UpgradePropensity(str, enum.Enum):
    LOW      = "low"
    MEDIUM   = "medium"
    HIGH     = "high"
    VERY_HIGH = "very_high"


# ── Tier config ───────────────────────────────────────────────────────────────

TIER_MONTHLY_FEES = {
    MemberTier.EXPLORER:  49.0,
    MemberTier.ACTIVE:    89.0,
    MemberTier.ELITE:    149.0,
    MemberTier.CHARTER:   69.0,  # legacy rate
    MemberTier.CORPORATE: 199.0,
}

TIER_ANNUAL_MULTIPLIER = 10.5   # Annual = monthly × 10.5 (saves ~12%)

CHURN_RISK_WEIGHTS = {
    "days_since_last_visit": 0.30,
    "visit_frequency_trend": 0.25,
    "payment_history":       0.20,
    "feature_utilization":   0.15,
    "nps_score":             0.10,
}


# ── ORM Models ────────────────────────────────────────────────────────────────

class MemberLTVScore(Base):
    """Lifetime value score and churn prediction for each member."""
    __tablename__ = "membership_ltv_scores"

    id: Mapped[str]              = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    member_id: Mapped[str]       = mapped_column(String(36), nullable=False, unique=True)  # FK to membership_ai members
    member_name: Mapped[str]     = mapped_column(String(200), nullable=False)
    member_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    tier: Mapped[str]            = mapped_column(SAEnum(MemberTier), nullable=False)
    monthly_fee: Mapped[float]   = mapped_column(Float, nullable=False)
    join_date: Mapped[date]      = mapped_column(Date, nullable=False)
    # LTV
    ltv_score: Mapped[int]       = mapped_column(Integer, nullable=False)      # 0–1000
    predicted_ltv_12mo: Mapped[float] = mapped_column(Float, nullable=False)  # $ next 12 months
    predicted_ltv_36mo: Mapped[float] = mapped_column(Float, nullable=False)  # $ next 36 months
    historical_revenue: Mapped[float] = mapped_column(Float, nullable=False)
    # Churn
    churn_probability_30d: Mapped[float] = mapped_column(Float, nullable=False)  # 0.0–1.0
    churn_probability_60d: Mapped[float] = mapped_column(Float, nullable=False)
    churn_probability_90d: Mapped[float] = mapped_column(Float, nullable=False)
    churn_risk_band: Mapped[str]         = mapped_column(SAEnum(ChurnRiskBand), nullable=False)
    # Engagement
    days_since_last_visit: Mapped[int]   = mapped_column(Integer, nullable=False)
    visits_last_30d: Mapped[int]         = mapped_column(Integer, default=0)
    visits_last_90d: Mapped[int]         = mapped_column(Integer, default=0)
    avg_monthly_visits: Mapped[float]    = mapped_column(Float, default=0.0)
    feature_utilization_pct: Mapped[float] = mapped_column(Float, default=0.0)
    nps_score: Mapped[Optional[int]]     = mapped_column(Integer, nullable=True)  # -100 to 100
    # Upgrade
    upgrade_propensity: Mapped[str]      = mapped_column(SAEnum(UpgradePropensity), default=UpgradePropensity.LOW)
    upgrade_target_tier: Mapped[Optional[str]] = mapped_column(SAEnum(MemberTier), nullable=True)
    # Meta
    last_scored_at: Mapped[datetime]     = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_at: Mapped[datetime]         = mapped_column(DateTime(timezone=True), server_default=func.now())

    win_back_sequences: Mapped[list["WinBackSequence"]] = relationship("WinBackSequence", back_populates="member_score", cascade="all, delete-orphan")


class ChurnPrediction(Base):
    """Point-in-time churn prediction log — historical model output."""
    __tablename__ = "churn_predictions"

    id: Mapped[str]              = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    member_id: Mapped[str]       = mapped_column(String(36), nullable=False)
    prediction_date: Mapped[date]= mapped_column(Date, nullable=False)
    churn_probability_30d: Mapped[float] = mapped_column(Float, nullable=False)
    churn_probability_60d: Mapped[float] = mapped_column(Float, nullable=False)
    churn_risk_band: Mapped[str] = mapped_column(SAEnum(ChurnRiskBand), nullable=False)
    feature_contributions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class WinBackSequence(Base):
    """Automated win-back outreach sequence for at-risk members."""
    __tablename__ = "winback_sequences"

    id: Mapped[str]              = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ltv_score_id: Mapped[str]    = mapped_column(ForeignKey("membership_ltv_scores.id"), nullable=False)
    member_id: Mapped[str]       = mapped_column(String(36), nullable=False)
    member_name: Mapped[str]     = mapped_column(String(200), nullable=False)
    tier: Mapped[str]            = mapped_column(SAEnum(MemberTier), nullable=False)
    churn_risk_band: Mapped[str] = mapped_column(SAEnum(ChurnRiskBand), nullable=False)
    revenue_at_risk: Mapped[float] = mapped_column(Float, nullable=False)
    offer_type: Mapped[str]      = mapped_column(String(100), nullable=False)
    offer_value: Mapped[float]   = mapped_column(Float, default=0.0)
    subject_line: Mapped[str]    = mapped_column(String(300), nullable=False)
    message_body: Mapped[str]    = mapped_column(Text, nullable=False)
    status: Mapped[str]          = mapped_column(SAEnum(WinBackStatus), default=WinBackStatus.PENDING)
    scheduled_send: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    sent_at: Mapped[Optional[datetime]]    = mapped_column(DateTime(timezone=True), nullable=True)
    opened_at: Mapped[Optional[datetime]]  = mapped_column(DateTime(timezone=True), nullable=True)
    converted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime]           = mapped_column(DateTime(timezone=True), server_default=func.now())

    member_score: Mapped["MemberLTVScore"] = relationship("MemberLTVScore", back_populates="win_back_sequences")


class MemberCohort(Base):
    """Cohort-level analysis — members grouped by join quarter and tier."""
    __tablename__ = "membership_cohorts"

    id: Mapped[str]              = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    cohort_label: Mapped[str]    = mapped_column(String(50), nullable=False)  # e.g. "2025-Q1-ACTIVE"
    tier: Mapped[str]            = mapped_column(SAEnum(MemberTier), nullable=False)
    join_quarter: Mapped[str]    = mapped_column(String(10), nullable=False)  # "2025-Q1"
    member_count: Mapped[int]    = mapped_column(Integer, nullable=False)
    avg_ltv_score: Mapped[float] = mapped_column(Float, nullable=False)
    avg_churn_30d: Mapped[float] = mapped_column(Float, nullable=False)
    retention_rate_90d: Mapped[float] = mapped_column(Float, nullable=False)
    avg_monthly_revenue: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# ── Pydantic ──────────────────────────────────────────────────────────────────

class WinBackCreate(BaseModel):
    member_id: str
    offer_type: str
    offer_value: float = 0.0


class LTVScoreUpdate(BaseModel):
    nps_score: Optional[int] = None
    days_since_last_visit: Optional[int] = None
    visits_last_30d: Optional[int] = None


# ── Scoring functions ─────────────────────────────────────────────────────────

def _compute_churn_probability(
    days_since_visit: int,
    visits_30d: int,
    visits_90d: int,
    months_member: int,
    feature_util: float,
    nps: Optional[int],
) -> tuple[float, float, float]:
    """Rule-based churn probability model — 0.0 to 1.0."""

    # Visit recency score (0–1, higher = more likely to churn)
    recency_score = min(1.0, days_since_visit / 60)

    # Frequency trend score
    expected_monthly = max(1.0, visits_90d / 3)
    freq_score = max(0.0, 1.0 - (visits_30d / expected_monthly)) if expected_monthly > 0 else 0.8

    # Feature utilization (lower util = higher churn risk)
    util_score = max(0.0, 1.0 - feature_util / 100)

    # NPS impact
    nps_score = 0.5 if nps is None else max(0.0, min(1.0, (50 - nps) / 100))

    # Tenure bonus (longer members less likely to churn)
    tenure_bonus = max(0.0, 0.3 - (months_member * 0.02))

    base_churn = (
        recency_score  * CHURN_RISK_WEIGHTS["days_since_last_visit"] +
        freq_score     * CHURN_RISK_WEIGHTS["visit_frequency_trend"] +
        util_score     * CHURN_RISK_WEIGHTS["feature_utilization"] +
        nps_score      * CHURN_RISK_WEIGHTS["nps_score"] +
        0.5            * CHURN_RISK_WEIGHTS["payment_history"]   # assume good payment
    ) + tenure_bonus

    p30 = round(min(0.95, max(0.02, base_churn)), 3)
    p60 = round(min(0.95, p30 * 1.25), 3)
    p90 = round(min(0.95, p60 * 1.15), 3)
    return p30, p60, p90


def _churn_band(p30: float) -> ChurnRiskBand:
    if p30 < 0.10:  return ChurnRiskBand.SAFE
    if p30 < 0.25:  return ChurnRiskBand.WATCH
    if p30 < 0.50:  return ChurnRiskBand.AT_RISK
    return ChurnRiskBand.CRITICAL


def _compute_ltv(monthly_fee: float, p_churn_30: float, months_member: int) -> tuple[int, float, float]:
    """Compute LTV score, 12mo prediction, 36mo prediction."""
    # Survival probability per month (simplified geometric)
    monthly_churn_rate = p_churn_30 / 3   # distribute 30d prob across ~3 months
    survival_12 = sum((1 - monthly_churn_rate) ** m for m in range(12))
    survival_36 = sum((1 - monthly_churn_rate) ** m for m in range(36))
    ltv_12 = round(monthly_fee * survival_12, 2)
    ltv_36 = round(monthly_fee * survival_36, 2)
    # Score: 0–1000 based on 36mo LTV relative to tier max
    tier_max_ltv = monthly_fee * 36  # perfect retention
    score = round(min(1000, (ltv_36 / tier_max_ltv) * 1000 + (months_member * 5)))
    return score, ltv_12, ltv_36


def _upgrade_propensity(visits_30d: int, feature_util: float, tier: MemberTier) -> tuple[UpgradePropensity, Optional[MemberTier]]:
    if tier in [MemberTier.ELITE, MemberTier.CHARTER, MemberTier.CORPORATE]:
        return UpgradePropensity.LOW, None
    if visits_30d >= 12 and feature_util >= 80:
        target = MemberTier.ELITE if tier == MemberTier.ACTIVE else MemberTier.ACTIVE
        return UpgradePropensity.VERY_HIGH, target
    if visits_30d >= 8 and feature_util >= 60:
        target = MemberTier.ELITE if tier == MemberTier.ACTIVE else MemberTier.ACTIVE
        return UpgradePropensity.HIGH, target
    if visits_30d >= 5:
        return UpgradePropensity.MEDIUM, None
    return UpgradePropensity.LOW, None


# ── DB dependency ─────────────────────────────────────────────────────────────

async def get_db() -> AsyncSession:
    raise NotImplementedError("Wire to your AsyncSession factory")


# ── Router ────────────────────────────────────────────────────────────────────

router = APIRouter(prefix="/api/membership-predictor", tags=["Membership Value Predictor"])
claude = Anthropic()

MP_CONTEXT = """
You are the AI membership strategist for NXS National Complex, Proctor MN.
NXS has Explorer ($49/mo), Active ($89/mo), Elite ($149/mo), Charter ($69/mo legacy),
and Corporate ($199/mo) membership tiers. Phase 1 target: $1.847M/yr complex revenue.
Membership retention and LTV maximization are core to sustainable revenue.
Provide specific, data-driven retention and upgrade recommendations.
"""

WIN_BACK_TEMPLATES = {
    ChurnRiskBand.AT_RISK: {
        "offer_type": "1-month_discount",
        "offer_value": 0.20,  # 20% off next month
        "subject_line": "We miss you at NXS — here's 20% off your next month",
    },
    ChurnRiskBand.CRITICAL: {
        "offer_type": "free_month",
        "offer_value": 1.0,  # 1 free month
        "subject_line": "Come back to NXS — your next month is on us",
    },
}


# ── Seed ──────────────────────────────────────────────────────────────────────

@router.post("/seed", summary="Seed 40 member LTV scores across all risk bands")
async def seed_membership_predictor(db: AsyncSession = Depends(get_db)) -> dict:
    existing = await db.scalar(select(func.count()).select_from(MemberLTVScore))
    if existing and existing > 0:
        return {"message": f"Already seeded — {existing} scores exist", "seeded": False}

    today = date.today()
    random.seed(123)

    member_configs = [
        # Safe members — high engagement
        ("Marcus Johnson",    "marcus@email.com",  MemberTier.ELITE,      today - timedelta(days=420), 3,  14, 42, 88, 72),
        ("Rivera Family",     "rivera@email.com",  MemberTier.ACTIVE,     today - timedelta(days=380), 2,  10, 30, 75, 60),
        ("Priya Patel",       "priya@email.com",   MemberTier.CHARTER,    today - timedelta(days=700), 1,  16, 48, 92, 80),
        ("Essentia Health",   "corp@essentia.com", MemberTier.CORPORATE,  today - timedelta(days=300), 5,  8,  24, 70, 55),
        ("Jake Nilsson",      "jake@email.com",    MemberTier.ACTIVE,     today - timedelta(days=250), 3,  12, 36, 85, 68),
        ("Angela Torres",     "angela@email.com",  MemberTier.ELITE,      today - timedelta(days=480), 2,  15, 44, 90, 78),
        ("Brian Gustafson",   "brian@email.com",   MemberTier.EXPLORER,   today - timedelta(days=120), 4,  9,  26, 72, 55),
        ("Imani Brooks",      "imani@email.com",   MemberTier.ACTIVE,     today - timedelta(days=340), 3,  11, 33, 80, 65),
        ("Connor Lindberg",   "connor@email.com",  MemberTier.ELITE,      today - timedelta(days=280), 2,  14, 40, 87, 74),
        ("Makena Okafor",     "makena@email.com",  MemberTier.ACTIVE,     today - timedelta(days=200), 4,  10, 29, 78, 62),
        # Watch band
        ("Tom Magnusson",     "tom@email.com",     MemberTier.ACTIVE,     today - timedelta(days=290), 18, 5,  15, 52, 40),
        ("Carla West",        "carla@email.com",   MemberTier.EXPLORER,   today - timedelta(days=180), 22, 4,  11, 45, 35),
        ("Nathan Lindqvist",  "nathan@email.com",  MemberTier.ACTIVE,     today - timedelta(days=320), 20, 6,  17, 55, 42),
        ("Devon Kowalski",    "devon@email.com",   MemberTier.ACTIVE,     today - timedelta(days=150), 25, 3,  9,  40, 30),
        ("Sierra Thompson",   "sierra@email.com",  MemberTier.EXPLORER,   today - timedelta(days=95),  19, 5,  13, 48, 38),
        # At risk
        ("Lakeview Coffee",   "coffee@lakeview.com", MemberTier.CORPORATE,today - timedelta(days=365), 35, 2,  6,  28, 22),
        ("Rachel Oberg",      "rachel@email.com",  MemberTier.ACTIVE,     today - timedelta(days=240), 40, 2,  5,  22, 18),
        ("Tyler Anderson",    "tyler@email.com",   MemberTier.EXPLORER,   today - timedelta(days=110), 38, 1,  4,  20, 15),
        ("Aaliyah Rivera",    "aaliyah@email.com", MemberTier.ACTIVE,     today - timedelta(days=195), 42, 1,  4,  18, 14),
        ("David Kowalski",    "david@email.com",   MemberTier.ELITE,      today - timedelta(days=450), 44, 2,  6,  25, 20),
        # Critical
        ("Zoe Magnusson",     "zoe@email.com",     MemberTier.EXPLORER,   today - timedelta(days=85),  55, 0,  2,  12, 10),
        ("Jordan Williams",   "jordan@email.com",  MemberTier.ACTIVE,     today - timedelta(days=310), 58, 1,  2,  10, 8),
        ("Fleet Farm Duluth", "ff@fleet.com",      MemberTier.CORPORATE,  today - timedelta(days=500), 62, 0,  1,  8,  6),
    ]

    # Add more safe members
    safe_names = [
        ("Amy Hanson","amy@email.com",MemberTier.ACTIVE,180,5,9,27,68,55),
        ("Craig Nelson","craig@email.com",MemberTier.EXPLORER,220,4,8,24,62,48),
        ("Beth Larson","beth@email.com",MemberTier.ELITE,520,2,13,38,85,70),
        ("Sean Murphy","sean@email.com",MemberTier.ACTIVE,280,6,10,30,74,60),
        ("Lisa Baker","lisa@email.com",MemberTier.ACTIVE,190,3,11,32,77,62),
        ("Kevin Young","kevin@email.com",MemberTier.CHARTER,680,1,15,44,91,80),
        ("Maya Wright","maya@email.com",MemberTier.ELITE,350,4,12,35,82,68),
        ("Tanya Allen","tanya@email.com",MemberTier.ACTIVE,240,3,9,26,70,56),
        ("Robert King","robert@email.com",MemberTier.EXPLORER,140,5,7,20,58,45),
        ("Jennifer Scott","jen@email.com",MemberTier.ACTIVE,260,2,10,29,75,60),
        ("Chris Adams","chris@email.com",MemberTier.ACTIVE,310,3,11,33,79,63),
        ("Pat Green","pat@email.com",MemberTier.EXPLORER,170,4,8,23,65,52),
        ("Dale Peterson","dale@email.com",MemberTier.ACTIVE,290,7,9,27,71,57),
        ("Raj Kumar","raj@email.com",MemberTier.ELITE,400,2,14,41,88,72),
        ("Eric Magnusson","eric@email.com",MemberTier.ACTIVE,220,3,10,30,76,61),
        ("Elsa Nilsson","elsa@email.com",MemberTier.CHARTER,730,1,14,42,93,82),
        ("Sven Lindqvist","sven@email.com",MemberTier.ACTIVE,195,4,9,27,69,55),
    ]
    for n,e,t,d,dsv,v30,v90,fu,nps in safe_names:
        member_configs.append((n,e,t,today-timedelta(days=d),dsv,v30,v90,fu,nps))

    created = []
    for (name, email, tier, join_date, days_since_visit, v30, v90, feature_util, nps) in member_configs:
        months_member = (today - join_date).days // 30
        monthly_fee = TIER_MONTHLY_FEES[tier]
        hist_rev = round(monthly_fee * months_member * random.uniform(0.9, 1.0), 2)

        p30, p60, p90 = _compute_churn_probability(days_since_visit, v30, v90, months_member, feature_util, nps)
        band = _churn_band(p30)
        ltv_score, ltv_12, ltv_36 = _compute_ltv(monthly_fee, p30, months_member)
        up_prop, up_target = _upgrade_propensity(v30, feature_util, tier)
        avg_visits = round(v90 / 3, 1)

        score = MemberLTVScore(
            member_id=str(uuid.uuid4()),
            member_name=name, member_email=email, tier=tier,
            monthly_fee=monthly_fee, join_date=join_date,
            ltv_score=ltv_score, predicted_ltv_12mo=ltv_12, predicted_ltv_36mo=ltv_36,
            historical_revenue=hist_rev,
            churn_probability_30d=p30, churn_probability_60d=p60, churn_probability_90d=p90,
            churn_risk_band=band,
            days_since_last_visit=days_since_visit,
            visits_last_30d=v30, visits_last_90d=v90, avg_monthly_visits=avg_visits,
            feature_utilization_pct=float(feature_util), nps_score=nps,
            upgrade_propensity=up_prop, upgrade_target_tier=up_target,
        )
        db.add(score)
        created.append(score)

    await db.flush()

    # Auto-generate win-back sequences for at-risk/critical
    wb_created = 0
    for score in created:
        if score.churn_risk_band in [ChurnRiskBand.AT_RISK, ChurnRiskBand.CRITICAL]:
            tmpl = WIN_BACK_TEMPLATES.get(score.churn_risk_band, WIN_BACK_TEMPLATES[ChurnRiskBand.AT_RISK])
            offer_val = round(score.monthly_fee * tmpl["offer_value"], 2)
            wb = WinBackSequence(
                ltv_score_id=score.id, member_id=score.member_id,
                member_name=score.member_name, tier=score.tier,
                churn_risk_band=score.churn_risk_band,
                revenue_at_risk=round(score.predicted_ltv_12mo, 2),
                offer_type=tmpl["offer_type"], offer_value=offer_val,
                subject_line=tmpl["subject_line"],
                message_body=f"Hi {score.member_name.split()[0]}, we've noticed you haven't visited NXS recently. "
                             f"As a valued {score.tier} member, we'd like to offer you "
                             f"{'a complimentary month' if score.churn_risk_band == ChurnRiskBand.CRITICAL else f'{int(tmpl[\"offer_value\"]*100)}% off your next month'}. "
                             f"Book your next session at NXS and remember why you joined. 704 Kirkus St, Proctor MN.",
                status=WinBackStatus.PENDING,
                scheduled_send=today + timedelta(days=1),
            )
            db.add(wb)
            wb_created += 1

    # Seed cohorts
    quarters = ["2024-Q3", "2024-Q4", "2025-Q1", "2025-Q2"]
    for q in quarters:
        for tier in [MemberTier.EXPLORER, MemberTier.ACTIVE, MemberTier.ELITE]:
            count = random.randint(8, 25)
            cohort = MemberCohort(
                cohort_label=f"{q}-{tier.value.upper()}",
                tier=tier, join_quarter=q, member_count=count,
                avg_ltv_score=random.randint(400, 850),
                avg_churn_30d=round(random.uniform(0.05, 0.35), 3),
                retention_rate_90d=round(random.uniform(0.68, 0.95), 3),
                avg_monthly_revenue=round(TIER_MONTHLY_FEES[tier] * random.uniform(0.85, 1.0), 2),
            )
            db.add(cohort)

    await db.commit()
    return {
        "message": "Membership Value Predictor seeded",
        "members_scored": len(member_configs),
        "win_back_sequences": wb_created,
        "cohorts": 12,
        "seeded": True,
    }


# ── LTV Scores ────────────────────────────────────────────────────────────────

@router.get("/ltv-scores", summary="Member LTV rankings — sorted by score or churn risk")
async def ltv_scores(
    tier: Optional[MemberTier] = Query(None),
    risk_band: Optional[ChurnRiskBand] = Query(None),
    sort_by: str = Query("ltv_score"),   # ltv_score, churn_probability_30d, predicted_ltv_12mo
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    q = select(MemberLTVScore)
    if tier:      q = q.where(MemberLTVScore.tier == tier)
    if risk_band: q = q.where(MemberLTVScore.churn_risk_band == risk_band)

    sort_col = getattr(MemberLTVScore, sort_by, MemberLTVScore.ltv_score)
    if sort_by == "churn_probability_30d":
        q = q.order_by(sort_col.desc())
    else:
        q = q.order_by(sort_col.desc())

    result = await db.execute(q)
    scores = result.scalars().all()
    return [
        {"id": s.id, "member_id": s.member_id, "member_name": s.member_name,
         "tier": s.tier, "monthly_fee": s.monthly_fee,
         "join_date": s.join_date.isoformat(),
         "ltv_score": s.ltv_score,
         "predicted_ltv_12mo": s.predicted_ltv_12mo,
         "predicted_ltv_36mo": s.predicted_ltv_36mo,
         "historical_revenue": s.historical_revenue,
         "churn_probability_30d": s.churn_probability_30d,
         "churn_probability_60d": s.churn_probability_60d,
         "churn_risk_band": s.churn_risk_band,
         "days_since_last_visit": s.days_since_last_visit,
         "visits_last_30d": s.visits_last_30d,
         "feature_utilization_pct": s.feature_utilization_pct,
         "nps_score": s.nps_score,
         "upgrade_propensity": s.upgrade_propensity,
         "upgrade_target_tier": s.upgrade_target_tier}
        for s in scores
    ]


# ── Churn Risk ────────────────────────────────────────────────────────────────

@router.get("/churn-risk", summary="At-risk and critical members with revenue exposure")
async def churn_risk_summary(db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(select(MemberLTVScore))
    all_scores = result.scalars().all()

    by_band: dict[str, list] = {b.value: [] for b in ChurnRiskBand}
    for s in all_scores:
        by_band[s.churn_risk_band.value].append(s)

    def _band_summary(members: list) -> dict:
        if not members:
            return {"count": 0, "revenue_at_risk_12mo": 0, "avg_churn_30d": 0}
        return {
            "count": len(members),
            "revenue_at_risk_12mo": round(sum(m.predicted_ltv_12mo for m in members), 2),
            "avg_churn_30d": round(sum(m.churn_probability_30d for m in members) / len(members), 3),
            "members": [{"member_name": m.member_name, "tier": m.tier, "monthly_fee": m.monthly_fee,
                          "churn_30d": m.churn_probability_30d, "ltv_12mo": m.predicted_ltv_12mo,
                          "days_since_visit": m.days_since_last_visit} for m in members[:10]],
        }

    total_at_risk = sum(m.predicted_ltv_12mo for m in by_band["at_risk"] + by_band["critical"])
    return {
        "bands": {band: _band_summary(members) for band, members in by_band.items()},
        "total_revenue_at_risk_12mo": round(total_at_risk, 2),
        "total_members": len(all_scores),
        "overall_churn_rate_30d": round(sum(s.churn_probability_30d for s in all_scores) / len(all_scores), 3) if all_scores else 0,
    }


# ── Win-Back ──────────────────────────────────────────────────────────────────

@router.post("/win-back-sequence", summary="Generate personalized win-back sequence for a member")
async def generate_win_back(payload: WinBackCreate, db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(select(MemberLTVScore).where(MemberLTVScore.member_id == payload.member_id))
    score = result.scalar_one_or_none()
    if not score:
        raise HTTPException(404, "Member score not found")

    tmpl = WIN_BACK_TEMPLATES.get(score.churn_risk_band, WIN_BACK_TEMPLATES[ChurnRiskBand.AT_RISK])
    offer_val = payload.offer_value or round(score.monthly_fee * tmpl["offer_value"], 2)

    wb = WinBackSequence(
        ltv_score_id=score.id, member_id=payload.member_id,
        member_name=score.member_name, tier=score.tier,
        churn_risk_band=score.churn_risk_band,
        revenue_at_risk=score.predicted_ltv_12mo,
        offer_type=payload.offer_type or tmpl["offer_type"],
        offer_value=offer_val,
        subject_line=tmpl["subject_line"],
        message_body=f"Hi {score.member_name.split()[0]}, we miss you at NXS! Come back and enjoy what you love.",
        status=WinBackStatus.PENDING,
        scheduled_send=date.today() + timedelta(days=1),
    )
    db.add(wb)
    await db.commit()
    return {"id": wb.id, "message": "Win-back sequence created"}


@router.get("/win-back-sequences", summary="List all win-back sequences with status")
async def list_win_back(
    status: Optional[WinBackStatus] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    q = select(WinBackSequence)
    if status: q = q.where(WinBackSequence.status == status)
    q = q.order_by(WinBackSequence.revenue_at_risk.desc())
    result = await db.execute(q)
    sequences = result.scalars().all()
    return [
        {"id": s.id, "member_name": s.member_name, "tier": s.tier,
         "churn_risk_band": s.churn_risk_band, "revenue_at_risk": s.revenue_at_risk,
         "offer_type": s.offer_type, "offer_value": s.offer_value,
         "subject_line": s.subject_line, "status": s.status,
         "scheduled_send": s.scheduled_send.isoformat() if s.scheduled_send else None}
        for s in sequences
    ]


# ── Cohort Analysis ───────────────────────────────────────────────────────────

@router.get("/cohort-analysis", summary="Cohort retention and LTV by join quarter and tier")
async def cohort_analysis(db: AsyncSession = Depends(get_db)) -> list[dict]:
    result = await db.execute(select(MemberCohort).order_by(MemberCohort.join_quarter, MemberCohort.tier))
    cohorts = result.scalars().all()
    return [
        {"cohort_label": c.cohort_label, "tier": c.tier, "join_quarter": c.join_quarter,
         "member_count": c.member_count, "avg_ltv_score": round(c.avg_ltv_score, 0),
         "avg_churn_30d": c.avg_churn_30d, "retention_rate_90d": c.retention_rate_90d,
         "avg_monthly_revenue": c.avg_monthly_revenue}
        for c in cohorts
    ]


# ── KPIs ──────────────────────────────────────────────────────────────────────

@router.get("/kpis", summary="Membership predictor KPI snapshot")
async def predictor_kpis(db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(select(MemberLTVScore))
    scores = result.scalars().all()

    if not scores:
        return {"error": "No scores — run seed first"}

    total_ltv_12 = sum(s.predicted_ltv_12mo for s in scores)
    total_ltv_36 = sum(s.predicted_ltv_36mo for s in scores)
    avg_score    = round(sum(s.ltv_score for s in scores) / len(scores))
    at_risk_rev  = sum(s.predicted_ltv_12mo for s in scores if s.churn_risk_band in [ChurnRiskBand.AT_RISK, ChurnRiskBand.CRITICAL])
    upgrade_candidates = [s for s in scores if s.upgrade_propensity in [UpgradePropensity.HIGH, UpgradePropensity.VERY_HIGH]]
    upgrade_revenue = sum((TIER_MONTHLY_FEES.get(s.upgrade_target_tier, s.monthly_fee) - s.monthly_fee) * 12 for s in upgrade_candidates if s.upgrade_target_tier)

    wb_result = await db.execute(select(func.count()).select_from(WinBackSequence).where(WinBackSequence.status == WinBackStatus.PENDING))
    pending_wb = wb_result.scalar() or 0

    tier_q = await db.execute(select(MemberLTVScore.tier, func.count(), func.avg(MemberLTVScore.ltv_score), func.avg(MemberLTVScore.churn_probability_30d)).group_by(MemberLTVScore.tier))
    tier_breakdown = {row[0]: {"count": row[1], "avg_ltv_score": round(row[2] or 0), "avg_churn_30d": round(row[3] or 0, 3)} for row in tier_q.all()}

    return {
        "total_members_scored": len(scores),
        "avg_ltv_score": avg_score,
        "total_predicted_ltv_12mo": round(total_ltv_12, 2),
        "total_predicted_ltv_36mo": round(total_ltv_36, 2),
        "revenue_at_risk_12mo": round(at_risk_rev, 2),
        "overall_churn_rate_30d": round(sum(s.churn_probability_30d for s in scores) / len(scores), 3),
        "upgrade_candidates": len(upgrade_candidates),
        "upgrade_annual_potential": round(upgrade_revenue, 2),
        "pending_win_back_sequences": pending_wb,
        "tier_breakdown": tier_breakdown,
        "band_counts": {
            b.value: sum(1 for s in scores if s.churn_risk_band == b)
            for b in ChurnRiskBand
        },
    }


# ── AI ────────────────────────────────────────────────────────────────────────

@router.post("/ai-brief", summary="AI membership retention and upgrade strategy brief")
async def ai_brief(db: AsyncSession = Depends(get_db)) -> dict:
    kpis = await predictor_kpis(db)
    risk = await churn_risk_summary(db)
    wb_q = await db.execute(select(WinBackSequence).where(WinBackSequence.status == WinBackStatus.PENDING).order_by(WinBackSequence.revenue_at_risk.desc()).limit(5))
    top_wb = wb_q.scalars().all()

    prompt = f"""
NXS Membership Predictor — Strategic Brief

PORTFOLIO:
- Members scored: {kpis['total_members_scored']}
- Avg LTV score: {kpis['avg_ltv_score']}/1000
- Predicted 12mo revenue: ${kpis['total_predicted_ltv_12mo']:,.0f}
- Predicted 36mo revenue: ${kpis['total_predicted_ltv_36mo']:,.0f}
- Revenue at risk (at-risk + critical): ${kpis['revenue_at_risk_12mo']:,.0f}
- Overall 30d churn rate: {kpis['overall_churn_rate_30d']*100:.1f}%

RISK BANDS:
- Safe: {kpis['band_counts']['safe']} members
- Watch: {kpis['band_counts']['watch']} members  
- At-Risk: {kpis['band_counts']['at_risk']} members
- Critical: {kpis['band_counts']['critical']} members

UPGRADE OPPORTUNITY:
- Candidates: {kpis['upgrade_candidates']} members with HIGH/VERY HIGH upgrade propensity
- Annual upgrade revenue potential: ${kpis['upgrade_annual_potential']:,.0f}

PENDING WIN-BACK SEQUENCES: {kpis['pending_win_back_sequences']}
Top revenue at risk (win-back targets):
{chr(10).join(f"  {w.member_name} ({w.tier}) — ${w.revenue_at_risk:,.0f} at risk, {w.churn_risk_band}" for w in top_wb)}

TIER PERFORMANCE:
{chr(10).join(f"  {k}: {v['count']} members, avg LTV {v['avg_ltv_score']}/1000, churn {v['avg_churn_30d']*100:.1f}%" for k, v in kpis['tier_breakdown'].items())}

Generate a 3-paragraph membership strategy brief:
1. Portfolio health — which tier is performing best/worst on retention and what does the at-risk revenue exposure mean in concrete terms?
2. Win-back priority — rank the top actions for this week. Which members to contact first, what to offer, and why those specific ones?
3. Upgrade strategy — how to activate the {kpis['upgrade_candidates']} upgrade candidates. What specific experience or trigger should push Explorer→Active or Active→Elite?
"""

    response = claude.messages.create(
        model="claude-opus-4-5",
        max_tokens=700,
        system=MP_CONTEXT,
        messages=[{"role": "user", "content": prompt}],
    )

    return {
        "brief": response.content[0].text,
        "kpis": kpis,
        "generated_at": datetime.utcnow().isoformat(),
    }
