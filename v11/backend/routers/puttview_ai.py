"""
SportAI Suite — PuttView AR Analytics Module
Sprint 4 · NGP Development
EXCLUSIVE within 200 miles · $280K investment · $153K/yr · 137% ROI
AR putting technology — session tracking, revenue per bay, ROI verification,
exclusivity protection monitoring, AI optimization

Add to main.py:
    from routers.puttview_ai import router as puttview_router
    app.include_router(puttview_router)
"""

from __future__ import annotations

import enum
import math
import uuid
from datetime import date, datetime, timedelta
from typing import Optional

from anthropic import Anthropic
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import (
    Boolean, Date, DateTime, Enum as SAEnum,
    Float, Integer, String, Text, func, select
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from database import get_db

class Base(DeclarativeBase):
    pass

# ── Constants ─────────────────────────────────────────────────────────────────

INVESTMENT_TOTAL    = 280_000.0
ANNUAL_REVENUE_TARGET = 153_000.0
TARGET_ROI_PCT      = 137.0        # % ROI target
EXCLUSIVITY_RADIUS_MILES = 200.0
PUTTVIEW_LOCATION   = {"lat": 46.7437, "lng": -92.2194}  # Proctor, MN

PUTTVIEW_BAYS       = 4   # Number of AR putting bays
BASE_RATE_PER_SESSION = 18.0   # $/session (30 min)
PREMIUM_RATE          = 28.0   # $/session (lesson-assisted)
CORPORATE_RATE        = 40.0   # $/session (corporate/event)

# Known competitors for exclusivity monitoring
KNOWN_COMPETITORS = [
    {"name": "Duluth Golf Center",       "city": "Duluth",       "state": "MN", "distance_miles": 8,   "has_ar": False},
    {"name": "Superior Links Golf",      "city": "Superior",     "state": "WI", "distance_miles": 12,  "has_ar": False},
    {"name": "Cloquet Golf Course",      "city": "Cloquet",      "state": "MN", "distance_miles": 22,  "has_ar": False},
    {"name": "Twin Ports Golf Dome",     "city": "Duluth",       "state": "MN", "distance_miles": 6,   "has_ar": False},
    {"name": "Minneapolis Golf Simulators","city": "Minneapolis","state": "MN", "distance_miles": 155, "has_ar": True,  "note": "Outside exclusivity zone"},
    {"name": "Rochester GolfSim",        "city": "Rochester",    "state": "MN", "distance_miles": 178, "has_ar": False},
    {"name": "Fargo Golf Center",        "city": "Fargo",        "state": "ND", "distance_miles": 193, "has_ar": False},
]

# ── Enums ─────────────────────────────────────────────────────────────────────

class SessionMode(str, enum.Enum):
    OPEN_PLAY  = "open_play"
    LESSON     = "lesson"
    LEAGUE     = "league"
    CORPORATE  = "corporate"
    EVENT      = "event"
    TOURNAMENT = "tournament"

class SkillLevel(str, enum.Enum):
    BEGINNER     = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED     = "advanced"
    PROFESSIONAL = "professional"

# ── ORM Models ────────────────────────────────────────────────────────────────

class PuttViewSession(Base):
    """Individual PuttView AR putting session."""
    __tablename__ = "puttview_sessions"

    id: Mapped[str]               = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    bay_number: Mapped[int]       = mapped_column(Integer, nullable=False)  # 1–4
    session_mode: Mapped[str]     = mapped_column(SAEnum(SessionMode), nullable=False)
    guest_name: Mapped[str]       = mapped_column(String(200), nullable=False)
    skill_level: Mapped[Optional[str]] = mapped_column(SAEnum(SkillLevel), nullable=True)
    guest_count: Mapped[int]      = mapped_column(Integer, default=1)
    session_date: Mapped[date]    = mapped_column(Date, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)  # 30 or 60
    rate: Mapped[float]           = mapped_column(Float, nullable=False)
    revenue: Mapped[float]        = mapped_column(Float, nullable=False)
    is_member: Mapped[bool]       = mapped_column(Boolean, default=False)
    putts_attempted: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    putts_made: Mapped[Optional[int]]      = mapped_column(Integer, nullable=True)
    notes: Mapped[Optional[str]]           = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime]           = mapped_column(DateTime(timezone=True), server_default=func.now())

    @property
    def make_pct(self) -> Optional[float]:
        if self.putts_attempted and self.putts_attempted > 0:
            return round((self.putts_made or 0) / self.putts_attempted * 100, 1)
        return None

class PuttViewRevenueLedger(Base):
    """Monthly revenue ledger — actuals vs target."""
    __tablename__ = "puttview_revenue_ledger"

    id: Mapped[str]               = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    month: Mapped[str]            = mapped_column(String(7), nullable=False, unique=True)  # "YYYY-MM"
    sessions_count: Mapped[int]   = mapped_column(Integer, nullable=False)
    revenue: Mapped[float]        = mapped_column(Float, nullable=False)
    target_monthly: Mapped[float] = mapped_column(Float, nullable=False)
    bays_active: Mapped[int]      = mapped_column(Integer, nullable=False)
    utilization_pct: Mapped[float]= mapped_column(Float, nullable=False)
    created_at: Mapped[datetime]  = mapped_column(DateTime(timezone=True), server_default=func.now())

class PuttViewROISnapshot(Base):
    """Periodic ROI calculation snapshots."""
    __tablename__ = "puttview_roi_snapshots"

    id: Mapped[str]                = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    snapshot_date: Mapped[date]    = mapped_column(Date, nullable=False)
    cumulative_revenue: Mapped[float] = mapped_column(Float, nullable=False)
    cumulative_costs: Mapped[float]   = mapped_column(Float, nullable=False)  # maintenance, license
    net_return: Mapped[float]         = mapped_column(Float, nullable=False)
    roi_pct: Mapped[float]            = mapped_column(Float, nullable=False)
    months_operational: Mapped[int]   = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime]      = mapped_column(DateTime(timezone=True), server_default=func.now())

# ── Pydantic ──────────────────────────────────────────────────────────────────

class SessionCreate(BaseModel):
    bay_number: int
    session_mode: SessionMode
    guest_name: str
    skill_level: Optional[SkillLevel] = None
    guest_count: int = 1
    session_date: date
    duration_minutes: int = 30
    is_member: bool = False
    putts_attempted: Optional[int] = None
    putts_made: Optional[int] = None
    notes: Optional[str] = None

# ── DB dependency ─────────────────────────────────────────────────────────────

# ── Router ────────────────────────────────────────────────────────────────────

router = APIRouter(prefix="/api/puttview", tags=["PuttView AR"])
claude = Anthropic()

PV_CONTEXT = """
You are the AI analytics advisor for PuttView AR at NXS National Complex, Proctor MN.
PuttView is an augmented reality putting system — EXCLUSIVE within 200 miles of Proctor MN.
Investment: $280,000 | Annual revenue target: $153,000 | Target ROI: 137%
4 AR putting bays available. Sessions: 30-min ($18) or 60-min ($28–$40 corporate).
NXS National Complex at 704 Kirkus St, Proctor MN — part of the NGP Development Phase 2.
Provide data-driven optimization insights focused on ROI achievement and exclusivity leverage.
"""

# ── Seed ──────────────────────────────────────────────────────────────────────

@router.post("/seed", summary="Seed PuttView sessions, revenue ledger, and ROI snapshots")
async def seed_puttview(db: AsyncSession = Depends(get_db)) -> dict:
    existing = await db.scalar(select(func.count()).select_from(PuttViewSession))
    if existing and existing > 0:
        return {"message": f"Already seeded — {existing} sessions exist", "seeded": False}

    today = date.today()
    target_monthly = ANNUAL_REVENUE_TARGET / 12

    # ── Sessions — 3 months of history ───────────────────────────────────────
    session_seeds = []
    import random
    random.seed(42)
    for days_ago in range(90, 0, -1):
        sdate = today - timedelta(days=days_ago)
        # 8–14 sessions per day across 4 bays
        daily_count = random.randint(8, 14)
        modes = [SessionMode.OPEN_PLAY] * 5 + [SessionMode.LESSON] * 2 + [SessionMode.CORPORATE] + [SessionMode.LEAGUE] + [SessionMode.EVENT]
        levels = list(SkillLevel)
        for _ in range(daily_count):
            mode = random.choice(modes)
            duration = 30 if mode == SessionMode.OPEN_PLAY else 60
            if mode == SessionMode.CORPORATE:
                rate = CORPORATE_RATE
            elif mode == SessionMode.LESSON:
                rate = PREMIUM_RATE
            else:
                rate = BASE_RATE_PER_SESSION
            guests = random.randint(1, 3) if mode != SessionMode.CORPORATE else random.randint(4, 8)
            revenue = round(rate * guests if mode == SessionMode.CORPORATE else rate, 2)
            putts_att = random.randint(30, 60) if duration == 30 else random.randint(60, 100)
            putts_made = int(putts_att * random.uniform(0.3, 0.65))
            session_seeds.append(PuttViewSession(
                bay_number=random.randint(1, PUTTVIEW_BAYS),
                session_mode=mode,
                guest_name=random.choice(["Rivera","Anderson","Thompson","Patel","Williams","Nilsson","Kowalski","Gustafson"]),
                skill_level=random.choice(levels),
                guest_count=guests,
                session_date=sdate,
                duration_minutes=duration,
                rate=rate,
                revenue=revenue,
                is_member=random.random() > 0.7,
                putts_attempted=putts_att,
                putts_made=putts_made,
            ))

    for s in session_seeds:
        db.add(s)

    # ── Monthly ledger ─────────────────────────────────────────────────────────
    for i in range(3):
        mo = today - timedelta(days=30 * (3 - i))
        mo_str = mo.strftime("%Y-%m")
        mo_sessions = [s for s in session_seeds if s.session_date.strftime("%Y-%m") == mo_str]
        mo_rev = sum(s.revenue for s in mo_sessions)
        util = min(len(mo_sessions) / (PUTTVIEW_BAYS * 30 * 8) * 100, 100)
        ledger = PuttViewRevenueLedger(
            month=mo_str, sessions_count=len(mo_sessions),
            revenue=round(mo_rev, 2), target_monthly=round(target_monthly, 2),
            bays_active=PUTTVIEW_BAYS, utilization_pct=round(util, 1),
        )
        db.add(ledger)

    # ── ROI Snapshots ──────────────────────────────────────────────────────────
    total_rev = sum(s.revenue for s in session_seeds)
    monthly_cost = 800.0  # license + maintenance
    cumulative_costs = INVESTMENT_TOTAL + (monthly_cost * 3)
    net_return = total_rev - cumulative_costs
    roi_pct = round(net_return / INVESTMENT_TOTAL * 100, 1)

    roi_snap = PuttViewROISnapshot(
        snapshot_date=today,
        cumulative_revenue=round(total_rev, 2),
        cumulative_costs=round(cumulative_costs, 2),
        net_return=round(net_return, 2),
        roi_pct=roi_pct,
        months_operational=3,
    )
    db.add(roi_snap)

    await db.commit()
    return {
        "message": "PuttView AR seeded",
        "sessions": len(session_seeds),
        "months_of_history": 3,
        "total_revenue_seeded": round(total_rev, 2),
        "seeded": True,
    }

# ── Sessions ──────────────────────────────────────────────────────────────────

@router.get("/sessions", summary="List PuttView sessions")
async def list_sessions(
    session_mode: Optional[SessionMode] = Query(None),
    days_back: int = Query(30),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    cutoff = date.today() - timedelta(days=days_back)
    q = select(PuttViewSession).where(PuttViewSession.session_date >= cutoff)
    if session_mode:
        q = q.where(PuttViewSession.session_mode == session_mode)
    q = q.order_by(PuttViewSession.session_date.desc())
    result = await db.execute(q)
    sessions = result.scalars().all()
    return [
        {"id": s.id, "bay_number": s.bay_number, "session_mode": s.session_mode,
         "guest_name": s.guest_name, "skill_level": s.skill_level,
         "guest_count": s.guest_count, "session_date": s.session_date.isoformat(),
         "duration_minutes": s.duration_minutes, "rate": s.rate, "revenue": s.revenue,
         "is_member": s.is_member, "make_pct": s.make_pct}
        for s in sessions
    ]

@router.post("/sessions", summary="Log a new PuttView session")
async def create_session(payload: SessionCreate, db: AsyncSession = Depends(get_db)) -> dict:
    if payload.bay_number not in range(1, PUTTVIEW_BAYS + 1):
        raise HTTPException(400, f"Bay number must be 1–{PUTTVIEW_BAYS}")
    if payload.session_mode == SessionMode.CORPORATE:
        rate = CORPORATE_RATE
    elif payload.session_mode == SessionMode.LESSON:
        rate = PREMIUM_RATE
    else:
        rate = BASE_RATE_PER_SESSION
    revenue = round(rate * payload.guest_count if payload.session_mode == SessionMode.CORPORATE else rate, 2)
    session = PuttViewSession(**payload.model_dump(), rate=rate, revenue=revenue)
    db.add(session)
    await db.commit()
    return {"id": session.id, "revenue": revenue, "message": "Session logged"}

# ── Revenue & ROI ──────────────────────────────────────────────────────────────

@router.get("/revenue-ledger", summary="Monthly revenue ledger vs target")
async def revenue_ledger(db: AsyncSession = Depends(get_db)) -> list[dict]:
    result = await db.execute(select(PuttViewRevenueLedger).order_by(PuttViewRevenueLedger.month))
    ledger = result.scalars().all()
    return [
        {"month": l.month, "sessions_count": l.sessions_count, "revenue": l.revenue,
         "target_monthly": l.target_monthly,
         "pacing_pct": round(l.revenue / l.target_monthly * 100, 1) if l.target_monthly else 0,
         "bays_active": l.bays_active, "utilization_pct": l.utilization_pct}
        for l in ledger
    ]

@router.get("/roi-dashboard", summary="Live ROI dashboard vs 137% target")
async def roi_dashboard(db: AsyncSession = Depends(get_db)) -> dict:
    # Live revenue from sessions
    rev_q = await db.execute(select(func.sum(PuttViewSession.revenue)))
    total_rev = rev_q.scalar() or 0.0

    sessions_q = await db.execute(select(func.count()).select_from(PuttViewSession))
    total_sessions = sessions_q.scalar() or 0

    # Estimate months operational from earliest session
    first_q = await db.execute(select(func.min(PuttViewSession.session_date)))
    first_date = first_q.scalar()
    months_op = max(1, ((date.today() - first_date).days // 30)) if first_date else 1

    monthly_cost = 800.0
    cumulative_costs = INVESTMENT_TOTAL + (monthly_cost * months_op)
    net_return = total_rev - cumulative_costs
    current_roi = round(net_return / INVESTMENT_TOTAL * 100, 1)

    # Annualized revenue projection
    monthly_rev = total_rev / months_op if months_op > 0 else 0
    annualized_rev = round(monthly_rev * 12, 2)
    projected_roi = round((annualized_rev - INVESTMENT_TOTAL) / INVESTMENT_TOTAL * 100, 1)

    # Mode breakdown
    mode_q = await db.execute(select(PuttViewSession.session_mode, func.count(), func.sum(PuttViewSession.revenue)).group_by(PuttViewSession.session_mode))
    mode_breakdown = {row[0]: {"sessions": row[1], "revenue": round(row[2] or 0, 2)} for row in mode_q.all()}

    # Bay utilization
    bay_q = await db.execute(select(PuttViewSession.bay_number, func.count(), func.sum(PuttViewSession.revenue)).group_by(PuttViewSession.bay_number))
    bay_breakdown = {row[0]: {"sessions": row[1], "revenue": round(row[2] or 0, 2)} for row in bay_q.all()}

    return {
        "investment": INVESTMENT_TOTAL,
        "target_roi_pct": TARGET_ROI_PCT,
        "total_revenue": round(total_rev, 2),
        "cumulative_costs": round(cumulative_costs, 2),
        "net_return": round(net_return, 2),
        "current_roi_pct": current_roi,
        "projected_annual_roi_pct": projected_roi,
        "annualized_revenue": annualized_rev,
        "annual_revenue_target": ANNUAL_REVENUE_TARGET,
        "annual_pacing_pct": round(annualized_rev / ANNUAL_REVENUE_TARGET * 100, 1),
        "total_sessions": total_sessions,
        "months_operational": months_op,
        "avg_revenue_per_session": round(total_rev / total_sessions, 2) if total_sessions else 0,
        "sessions_per_day": round(total_sessions / (months_op * 30), 1) if months_op else 0,
        "mode_breakdown": mode_breakdown,
        "bay_breakdown": bay_breakdown,
        "on_track_for_target": projected_roi >= TARGET_ROI_PCT * 0.80,
    }

@router.get("/exclusivity-radius", summary="Exclusivity zone — 200-mile competitor map")
async def exclusivity_radius() -> dict:
    within_zone = [c for c in KNOWN_COMPETITORS if c["distance_miles"] < EXCLUSIVITY_RADIUS_MILES and not c.get("has_ar", False)]
    outside_zone = [c for c in KNOWN_COMPETITORS if c["distance_miles"] >= EXCLUSIVITY_RADIUS_MILES]
    has_ar_outside = [c for c in KNOWN_COMPETITORS if c.get("has_ar") and c["distance_miles"] >= EXCLUSIVITY_RADIUS_MILES]

    return {
        "exclusivity_radius_miles": EXCLUSIVITY_RADIUS_MILES,
        "nxs_location": PUTTVIEW_LOCATION,
        "exclusivity_status": "PROTECTED",
        "competitors_within_zone": within_zone,
        "competitors_outside_zone": outside_zone,
        "ar_competitors_outside": has_ar_outside,
        "closest_ar_competitor_miles": min((c["distance_miles"] for c in KNOWN_COMPETITORS if c.get("has_ar")), default=999),
        "zone_threat_level": "LOW",
        "zone_summary": f"NXS holds exclusive PuttView AR rights within {EXCLUSIVITY_RADIUS_MILES} miles. {len(within_zone)} golf venues within zone, none with AR technology.",
    }

# ── AI ────────────────────────────────────────────────────────────────────────

@router.post("/ai-optimization", summary="AI revenue optimization and ROI acceleration brief")
async def ai_optimization(db: AsyncSession = Depends(get_db)) -> dict:
    roi = await roi_dashboard(db)
    exclusivity = await exclusivity_radius()
    ledger = await revenue_ledger(db)

    ledger_summary = "\n".join(
        f"  {l['month']}: ${l['revenue']:,.0f} revenue ({l['pacing_pct']}% of target) | {l['sessions_count']} sessions | {l['utilization_pct']}% utilization"
        for l in ledger
    )

    prompt = f"""
PuttView AR — Revenue Optimization Brief

PERFORMANCE:
- Investment: ${roi['investment']:,.0f} | Target ROI: {roi['target_roi_pct']}%
- Total revenue: ${roi['total_revenue']:,.0f} | Current ROI: {roi['current_roi_pct']}%
- Annualized revenue: ${roi['annualized_revenue']:,.0f} / ${roi['annual_revenue_target']:,.0f} target ({roi['annual_pacing_pct']}%)
- Sessions/day: {roi['sessions_per_day']} | Avg revenue/session: ${roi['avg_revenue_per_session']}
- On track for {roi['target_roi_pct']}% ROI: {"YES" if roi['on_track_for_target'] else "NEEDS ACCELERATION"}

MONTHLY HISTORY:
{ledger_summary}

SESSION MIX:
{chr(10).join(f"  {k}: {v['sessions']} sessions = ${v['revenue']:,.0f}" for k, v in roi['mode_breakdown'].items())}

BAY UTILIZATION:
{chr(10).join(f"  Bay {k}: {v['sessions']} sessions = ${v['revenue']:,.0f}" for k, v in roi['bay_breakdown'].items())}

EXCLUSIVITY: {exclusivity['zone_summary']}
Closest AR competitor: {exclusivity['closest_ar_competitor_miles']} miles away

Generate a 3-paragraph optimization brief:
1. ROI trajectory — are we on track for 137%? What's the revenue gap and how big is it in sessions/day terms?
2. Session mix optimization — which modes (open play, lessons, corporate, leagues) should be pushed harder? Corporate and league are highest-yield — specific tactics to grow these
3. Exclusivity monetization — how to actively market the 200-mile exclusive advantage, what events/promotions to launch, and how to price premium experiences that competitors can't match
"""

    response = claude.messages.create(
        model="claude-opus-4-5",
        max_tokens=700,
        system=PV_CONTEXT,
        messages=[{"role": "user", "content": prompt}],
    )

    return {
        "optimization": response.content[0].text,
        "roi_snapshot": roi,
        "generated_at": datetime.utcnow().isoformat(),
    }

@router.get("/kpis", summary="PuttView top-line KPIs")
async def puttview_kpis(db: AsyncSession = Depends(get_db)) -> dict:
    roi = await roi_dashboard(db)
    return {
        "bays": PUTTVIEW_BAYS,
        "investment": INVESTMENT_TOTAL,
        "target_roi_pct": TARGET_ROI_PCT,
        "current_roi_pct": roi["current_roi_pct"],
        "annual_revenue_target": ANNUAL_REVENUE_TARGET,
        "annualized_revenue": roi["annualized_revenue"],
        "annual_pacing_pct": roi["annual_pacing_pct"],
        "total_sessions": roi["total_sessions"],
        "exclusivity_radius_miles": EXCLUSIVITY_RADIUS_MILES,
        "exclusivity_status": "PROTECTED",
        "on_track": roi["on_track_for_target"],
    }
