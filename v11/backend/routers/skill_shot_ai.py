"""
SportAI Suite — Skill Shot Academy Module
Sprint 4 · NGP Development — Phase 2 Flagship
$4.65M investment · TrackMan 10 bays · Year 3 launch
Capital: SBA 504 $2M + Naming Rights $1M + State Grants $750K + Crowdfunding $900K
Target: $3.8M Year 1 revenue

Add to main.py:
    from routers.skill_shot_ai import router as skill_shot_router
    app.include_router(skill_shot_router)
"""

from __future__ import annotations

import enum
import uuid
from datetime import date, datetime, timedelta
from typing import Optional

from anthropic import Anthropic
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import (
    Boolean, Date, DateTime, Enum as SAEnum,
    Float, ForeignKey, Integer, String, Text, func, select
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from database import get_db

class Base(DeclarativeBase):
    pass

# ── Enums ─────────────────────────────────────────────────────────────────────

class BayStatus(str, enum.Enum):
    PLANNED      = "planned"
    INSTALLATION = "installation"
    CALIBRATION  = "calibration"
    OPERATIONAL  = "operational"
    MAINTENANCE  = "maintenance"

class SessionType(str, enum.Enum):
    INDIVIDUAL   = "individual"
    GROUP        = "group"
    LESSON       = "lesson"
    LEAGUE       = "league"
    CORPORATE    = "corporate"
    SIMULATOR    = "simulator"

class MilestoneStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED   = "completed"
    AT_RISK     = "at_risk"
    BLOCKED     = "blocked"

class CapitalSource(str, enum.Enum):
    SBA_504        = "sba_504"
    NAMING_RIGHTS  = "naming_rights"
    STATE_GRANTS   = "state_grants"
    CROWDFUNDING   = "crowdfunding"
    OPERATING      = "operating_cash"
    OTHER          = "other"

# ── Capital plan ───────────────────────────────────────────────────────────────

CAPITAL_PLAN = {
    CapitalSource.SBA_504:       {"target": 2_000_000.0, "label": "SBA 504 Loan"},
    CapitalSource.NAMING_RIGHTS: {"target": 1_000_000.0, "label": "Naming Rights / Sponsorship"},
    CapitalSource.STATE_GRANTS:  {"target":   750_000.0, "label": "State Grants (IRRRB / MN DEED)"},
    CapitalSource.CROWDFUNDING:  {"target":   900_000.0, "label": "Community Crowdfunding"},
}
TOTAL_INVESTMENT = 4_650_000.0
YEAR1_REVENUE_TARGET = 3_800_000.0

TRACKMAN_BAYS = 10
BAY_RATE = {
    SessionType.INDIVIDUAL: 45.0,   # $/hr
    SessionType.GROUP:      35.0,   # $/hr per person
    SessionType.LESSON:     85.0,   # $/hr (instructor included)
    SessionType.LEAGUE:     30.0,   # $/hr per person
    SessionType.CORPORATE:  60.0,   # $/hr
    SessionType.SIMULATOR:  50.0,   # $/hr
}

# ── ORM Models ────────────────────────────────────────────────────────────────

class SkillShotBay(Base):
    """One of the 10 TrackMan bays in the Skill Shot Academy."""
    __tablename__ = "skill_shot_bays"

    id: Mapped[str]              = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    bay_number: Mapped[int]      = mapped_column(Integer, nullable=False, unique=True)
    status: Mapped[str]          = mapped_column(SAEnum(BayStatus), default=BayStatus.PLANNED)
    trackman_serial: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    installation_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    operational_date: Mapped[Optional[date]]  = mapped_column(Date, nullable=True)
    sessions_total: Mapped[int]  = mapped_column(Integer, default=0)
    revenue_total: Mapped[float] = mapped_column(Float, default=0.0)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool]      = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    sessions: Mapped[list["SkillShotSession"]] = relationship("SkillShotSession", back_populates="bay", cascade="all, delete-orphan")

class SkillShotSession(Base):
    """Booked session in a TrackMan bay."""
    __tablename__ = "skill_shot_sessions"

    id: Mapped[str]               = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    bay_id: Mapped[str]           = mapped_column(ForeignKey("skill_shot_bays.id"), nullable=False)
    session_type: Mapped[str]     = mapped_column(SAEnum(SessionType), nullable=False)
    guest_name: Mapped[str]       = mapped_column(String(200), nullable=False)
    guest_count: Mapped[int]      = mapped_column(Integer, default=1)
    session_date: Mapped[date]    = mapped_column(Date, nullable=False)
    duration_hours: Mapped[float] = mapped_column(Float, nullable=False)
    rate_per_hour: Mapped[float]  = mapped_column(Float, nullable=False)
    revenue: Mapped[float]        = mapped_column(Float, nullable=False)
    instructor_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    is_member: Mapped[bool]       = mapped_column(Boolean, default=False)
    notes: Mapped[Optional[str]]  = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime]  = mapped_column(DateTime(timezone=True), server_default=func.now())

    bay: Mapped["SkillShotBay"] = relationship("SkillShotBay", back_populates="sessions")

class SkillShotMilestone(Base):
    """Phase 2 launch milestone tracking."""
    __tablename__ = "skill_shot_milestones"

    id: Mapped[str]               = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    phase: Mapped[int]            = mapped_column(Integer, nullable=False)  # 1=planning, 2=build, 3=launch
    title: Mapped[str]            = mapped_column(String(300), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str]           = mapped_column(SAEnum(MilestoneStatus), default=MilestoneStatus.NOT_STARTED)
    target_date: Mapped[Optional[date]]    = mapped_column(Date, nullable=True)
    completed_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    owner: Mapped[Optional[str]]           = mapped_column(String(200), nullable=True)
    progress_pct: Mapped[int]              = mapped_column(Integer, default=0)
    blockers: Mapped[Optional[str]]        = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime]           = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime]           = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class SkillShotCapital(Base):
    """Capital source tracking — committed, received, deployed."""
    __tablename__ = "skill_shot_capital"

    id: Mapped[str]               = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source: Mapped[str]           = mapped_column(SAEnum(CapitalSource), nullable=False, unique=True)
    label: Mapped[str]            = mapped_column(String(200), nullable=False)
    target_amount: Mapped[float]  = mapped_column(Float, nullable=False)
    committed_amount: Mapped[float] = mapped_column(Float, default=0.0)
    received_amount: Mapped[float]  = mapped_column(Float, default=0.0)
    deployed_amount: Mapped[float]  = mapped_column(Float, default=0.0)
    status: Mapped[str]           = mapped_column(String(50), default="pending")
    notes: Mapped[Optional[str]]  = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime]  = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    @property
    def committed_pct(self) -> float:
        return round(self.committed_amount / self.target_amount * 100, 1) if self.target_amount else 0

    @property
    def gap(self) -> float:
        return round(self.target_amount - self.committed_amount, 2)

# ── Pydantic ──────────────────────────────────────────────────────────────────

class SessionCreate(BaseModel):
    bay_id: str
    session_type: SessionType
    guest_name: str
    guest_count: int = 1
    session_date: date
    duration_hours: float
    instructor_name: Optional[str] = None
    is_member: bool = False
    notes: Optional[str] = None

class MilestoneUpdate(BaseModel):
    status: Optional[MilestoneStatus] = None
    progress_pct: Optional[int] = None
    completed_date: Optional[date] = None
    blockers: Optional[str] = None
    notes: Optional[str] = None

class CapitalUpdate(BaseModel):
    committed_amount: Optional[float] = None
    received_amount: Optional[float] = None
    deployed_amount: Optional[float] = None
    status: Optional[str] = None
    notes: Optional[str] = None

# ── DB dependency ─────────────────────────────────────────────────────────────

# ── Router ────────────────────────────────────────────────────────────────────

router = APIRouter(prefix="/api/skill-shot", tags=["Skill Shot Academy"])
claude = Anthropic()

SS_CONTEXT = """
You are the AI strategic advisor for Skill Shot Academy at NXS National Complex, Proctor MN.
Phase 2 investment: $4.65M | Year 1 revenue target: $3.8M
Technology: 10 TrackMan simulator bays — the most advanced golf/sports simulation tech available.
Capital stack: SBA 504 $2M + Naming Rights $1M + State Grants $750K + Crowdfunding $900K.
NGP Development is the entity. NXS National Complex is the operating campus.
Year 3 launch (relative to NXS Phase 1 operational start).
Provide specific, investor-quality strategic insights and launch readiness assessments.
"""

# ── Seed ──────────────────────────────────────────────────────────────────────

@router.post("/seed", summary="Seed 10 TrackMan bays, milestones, capital plan, and sample sessions")
async def seed_skill_shot(db: AsyncSession = Depends(get_db)) -> dict:
    existing = await db.scalar(select(func.count()).select_from(SkillShotBay))
    if existing and existing > 0:
        return {"message": f"Already seeded — {existing} bays exist", "seeded": False}

    today = date.today()

    # ── 10 TrackMan bays ──────────────────────────────────────────────────────
    bay_configs = [
        (BayStatus.OPERATIONAL, today - timedelta(days=90),  today - timedelta(days=60),  "TM-SS-001"),
        (BayStatus.OPERATIONAL, today - timedelta(days=90),  today - timedelta(days=60),  "TM-SS-002"),
        (BayStatus.OPERATIONAL, today - timedelta(days=60),  today - timedelta(days=30),  "TM-SS-003"),
        (BayStatus.CALIBRATION, today - timedelta(days=30),  None,                         "TM-SS-004"),
        (BayStatus.CALIBRATION, today - timedelta(days=30),  None,                         "TM-SS-005"),
        (BayStatus.INSTALLATION,today - timedelta(days=14),  None,                         "TM-SS-006"),
        (BayStatus.INSTALLATION,today - timedelta(days=14),  None,                         "TM-SS-007"),
        (BayStatus.PLANNED,     None,                         None,                         None),
        (BayStatus.PLANNED,     None,                         None,                         None),
        (BayStatus.PLANNED,     None,                         None,                         None),
    ]

    created_bays = []
    for i, (status, install_date, op_date, serial) in enumerate(bay_configs, start=1):
        bay = SkillShotBay(
            bay_number=i, status=status,
            trackman_serial=serial,
            installation_date=install_date,
            operational_date=op_date,
        )
        db.add(bay)
        created_bays.append(bay)

    await db.flush()

    # ── Sample sessions for operational bays ──────────────────────────────────
    operational_bays = [b for b in created_bays if b.status == BayStatus.OPERATIONAL]
    session_seeds = [
        (0, SessionType.INDIVIDUAL, "Marcus Williams",  1, today - timedelta(days=5),  1.5),
        (0, SessionType.LESSON,     "Priya Patel",       1, today - timedelta(days=4),  1.0),
        (1, SessionType.GROUP,      "Duluth Golf Group", 4, today - timedelta(days=3),  2.0),
        (0, SessionType.CORPORATE,  "Essentia Health",   8, today - timedelta(days=2),  2.0),
        (1, SessionType.INDIVIDUAL, "Jake Nilsson",      1, today - timedelta(days=1),  1.0),
        (2, SessionType.SIMULATOR,  "Anderson Family",   3, today,                      2.0),
        (0, SessionType.LEAGUE,     "NXS Tuesday League",6, today + timedelta(days=1),  3.0),
        (1, SessionType.INDIVIDUAL, "Rivera, Sarah",     1, today + timedelta(days=2),  1.5),
        (2, SessionType.LESSON,     "Thompson, Dale",    1, today + timedelta(days=3),  1.0),
        (0, SessionType.CORPORATE,  "Fleet Farm Team",  10, today + timedelta(days=5),  3.0),
    ]

    for bay_idx, stype, guest, count, sdate, hrs in session_seeds:
        if bay_idx >= len(operational_bays):
            continue
        bay = operational_bays[bay_idx]
        rate = BAY_RATE[stype]
        revenue = round(rate * hrs * (count if stype in [SessionType.GROUP, SessionType.LEAGUE] else 1), 2)
        session = SkillShotSession(
            bay_id=bay.id, session_type=stype, guest_name=guest,
            guest_count=count, session_date=sdate,
            duration_hours=hrs, rate_per_hour=rate, revenue=revenue,
            instructor_name="Coach Mike Larson" if stype == SessionType.LESSON else None,
        )
        db.add(session)
        bay.sessions_total += 1
        bay.revenue_total  += revenue

    # ── Launch milestones ─────────────────────────────────────────────────────
    milestones = [
        # Phase 1 — Planning & Capital
        SkillShotMilestone(phase=1, title="SBA 504 Loan Application Submitted",         status=MilestoneStatus.COMPLETED,   progress_pct=100, target_date=today - timedelta(days=180), completed_date=today - timedelta(days=175), owner="Shaun Marline"),
        SkillShotMilestone(phase=1, title="SBA 504 Loan Approved — $2M",                status=MilestoneStatus.COMPLETED,   progress_pct=100, target_date=today - timedelta(days=120), completed_date=today - timedelta(days=110), owner="Shaun Marline"),
        SkillShotMilestone(phase=1, title="Naming Rights Partner — $1M Commitment",     status=MilestoneStatus.IN_PROGRESS, progress_pct=65,  target_date=today + timedelta(days=60),  owner="Shaun Marline", blockers="Final negotiation phase — two regional candidates"),
        SkillShotMilestone(phase=1, title="State Grant Applications (IRRRB + MN DEED)", status=MilestoneStatus.IN_PROGRESS, progress_pct=70,  target_date=today + timedelta(days=45),  owner="Shaun Marline"),
        SkillShotMilestone(phase=1, title="Crowdfunding Campaign Launch — $900K",       status=MilestoneStatus.NOT_STARTED, progress_pct=0,   target_date=today + timedelta(days=90),  owner="Marketing Team"),
        # Phase 2 — Build
        SkillShotMilestone(phase=2, title="TrackMan Equipment Order (10 units)",        status=MilestoneStatus.COMPLETED,   progress_pct=100, target_date=today - timedelta(days=90),  completed_date=today - timedelta(days=85), owner="Operations"),
        SkillShotMilestone(phase=2, title="Bays 1–3 Installation & Commissioning",      status=MilestoneStatus.COMPLETED,   progress_pct=100, target_date=today - timedelta(days=60),  completed_date=today - timedelta(days=55), owner="ISG Engineering"),
        SkillShotMilestone(phase=2, title="Bays 4–7 Installation",                      status=MilestoneStatus.IN_PROGRESS, progress_pct=50,  target_date=today + timedelta(days=30),  owner="ISG Engineering"),
        SkillShotMilestone(phase=2, title="Bays 8–10 Installation",                     status=MilestoneStatus.NOT_STARTED, progress_pct=0,   target_date=today + timedelta(days=90),  owner="ISG Engineering"),
        SkillShotMilestone(phase=2, title="Staff Hiring — 6 Instructors + 2 Ops",      status=MilestoneStatus.IN_PROGRESS, progress_pct=40,  target_date=today + timedelta(days=60),  owner="HR"),
        SkillShotMilestone(phase=2, title="Membership Program Design & Launch",         status=MilestoneStatus.NOT_STARTED, progress_pct=0,   target_date=today + timedelta(days=75),  owner="Marketing"),
        # Phase 3 — Launch
        SkillShotMilestone(phase=3, title="Soft Launch — Bays 1–7 (Invite-Only)",      status=MilestoneStatus.NOT_STARTED, progress_pct=0,   target_date=today + timedelta(days=45),  owner="Shaun Marline"),
        SkillShotMilestone(phase=3, title="Grand Opening — All 10 Bays",               status=MilestoneStatus.NOT_STARTED, progress_pct=0,   target_date=today + timedelta(days=120), owner="Shaun Marline"),
        SkillShotMilestone(phase=3, title="Year 1 Revenue Target — $3.8M",             status=MilestoneStatus.NOT_STARTED, progress_pct=0,   target_date=today + timedelta(days=365), owner="Shaun Marline"),
        SkillShotMilestone(phase=3, title="Naming Rights Signage & Activation",        status=MilestoneStatus.NOT_STARTED, progress_pct=0,   target_date=today + timedelta(days=130), owner="Marketing"),
    ]
    for m in milestones:
        db.add(m)

    # ── Capital tracker ───────────────────────────────────────────────────────
    capital_seeds = [
        SkillShotCapital(source=CapitalSource.SBA_504,       label="SBA 504 Loan",              target_amount=2_000_000, committed_amount=2_000_000, received_amount=1_200_000, deployed_amount=900_000, status="approved"),
        SkillShotCapital(source=CapitalSource.NAMING_RIGHTS, label="Naming Rights / Sponsorship", target_amount=1_000_000, committed_amount=650_000,  received_amount=250_000,  deployed_amount=0,       status="in_negotiation", notes="Two regional candidates — final LOI stage"),
        SkillShotCapital(source=CapitalSource.STATE_GRANTS,  label="State Grants (IRRRB/DEED)",  target_amount=750_000,   committed_amount=350_000,  received_amount=0,        deployed_amount=0,       status="applications_submitted"),
        SkillShotCapital(source=CapitalSource.CROWDFUNDING,  label="Community Crowdfunding",      target_amount=900_000,   committed_amount=0,        received_amount=0,        deployed_amount=0,       status="pending_launch"),
    ]
    for cap in capital_seeds:
        db.add(cap)

    await db.commit()
    return {
        "message": "Skill Shot Academy seeded",
        "bays": 10, "sessions": len(session_seeds),
        "milestones": len(milestones), "capital_sources": len(capital_seeds),
        "seeded": True,
    }

# ── Bays ──────────────────────────────────────────────────────────────────────

@router.get("/bays", summary="List all 10 TrackMan bays with status")
async def list_bays(db: AsyncSession = Depends(get_db)) -> list[dict]:
    result = await db.execute(select(SkillShotBay).order_by(SkillShotBay.bay_number))
    bays = result.scalars().unique().all()
    return [
        {"id": b.id, "bay_number": b.bay_number, "status": b.status,
         "trackman_serial": b.trackman_serial,
         "installation_date": b.installation_date.isoformat() if b.installation_date else None,
         "operational_date": b.operational_date.isoformat() if b.operational_date else None,
         "sessions_total": b.sessions_total, "revenue_total": round(b.revenue_total, 2)}
        for b in bays
    ]

# ── Sessions ──────────────────────────────────────────────────────────────────

@router.get("/sessions", summary="List sessions with optional filters")
async def list_sessions(
    session_type: Optional[SessionType] = Query(None),
    days_back: int = Query(30),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    cutoff = date.today() - timedelta(days=days_back)
    q = select(SkillShotSession).where(SkillShotSession.session_date >= cutoff)
    if session_type:
        q = q.where(SkillShotSession.session_type == session_type)
    q = q.order_by(SkillShotSession.session_date.desc())
    result = await db.execute(q)
    sessions = result.scalars().all()
    return [
        {"id": s.id, "bay_id": s.bay_id, "session_type": s.session_type,
         "guest_name": s.guest_name, "guest_count": s.guest_count,
         "session_date": s.session_date.isoformat(), "duration_hours": s.duration_hours,
         "rate_per_hour": s.rate_per_hour, "revenue": s.revenue, "is_member": s.is_member}
        for s in sessions
    ]

@router.post("/sessions", summary="Book a new session")
async def create_session(payload: SessionCreate, db: AsyncSession = Depends(get_db)) -> dict:
    rate = BAY_RATE[payload.session_type]
    multiplier = payload.guest_count if payload.session_type in [SessionType.GROUP, SessionType.LEAGUE] else 1
    revenue = round(rate * payload.duration_hours * multiplier, 2)
    session = SkillShotSession(**payload.model_dump(), rate_per_hour=rate, revenue=revenue)
    db.add(session)
    await db.commit()
    return {"id": session.id, "revenue": revenue, "message": "Session booked"}

# ── Milestones ────────────────────────────────────────────────────────────────

@router.get("/milestones", summary="Launch milestone tracker")
async def list_milestones(phase: Optional[int] = Query(None), db: AsyncSession = Depends(get_db)) -> list[dict]:
    q = select(SkillShotMilestone).order_by(SkillShotMilestone.phase, SkillShotMilestone.target_date)
    if phase:
        q = q.where(SkillShotMilestone.phase == phase)
    result = await db.execute(q)
    milestones = result.scalars().all()
    return [
        {"id": m.id, "phase": m.phase, "title": m.title, "status": m.status,
         "progress_pct": m.progress_pct,
         "target_date": m.target_date.isoformat() if m.target_date else None,
         "completed_date": m.completed_date.isoformat() if m.completed_date else None,
         "owner": m.owner, "blockers": m.blockers, "description": m.description}
        for m in milestones
    ]

@router.patch("/milestones/{milestone_id}", summary="Update milestone status")
async def update_milestone(milestone_id: str, payload: MilestoneUpdate, db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(select(SkillShotMilestone).where(SkillShotMilestone.id == milestone_id))
    m = result.scalar_one_or_none()
    if not m:
        raise HTTPException(404, "Milestone not found")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(m, k, v)
    await db.commit()
    return {"id": m.id, "message": "Milestone updated"}

# ── Capital Stack ─────────────────────────────────────────────────────────────

@router.get("/capital-stack", summary="Capital stack — committed, received, deployed by source")
async def capital_stack(db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(select(SkillShotCapital))
    sources = result.scalars().all()

    total_target    = sum(s.target_amount    for s in sources)
    total_committed = sum(s.committed_amount for s in sources)
    total_received  = sum(s.received_amount  for s in sources)
    total_deployed  = sum(s.deployed_amount  for s in sources)

    return {
        "total_investment": TOTAL_INVESTMENT,
        "total_target": round(total_target, 2),
        "total_committed": round(total_committed, 2),
        "total_received": round(total_received, 2),
        "total_deployed": round(total_deployed, 2),
        "committed_pct": round(total_committed / total_target * 100, 1) if total_target else 0,
        "received_pct":  round(total_received  / total_target * 100, 1) if total_target else 0,
        "deployed_pct":  round(total_deployed  / total_target * 100, 1) if total_target else 0,
        "gap_to_close": round(total_target - total_committed, 2),
        "sources": [
            {"id": s.id, "source": s.source, "label": s.label,
             "target_amount": s.target_amount, "committed_amount": s.committed_amount,
             "received_amount": s.received_amount, "deployed_amount": s.deployed_amount,
             "committed_pct": s.committed_pct, "gap": s.gap, "status": s.status, "notes": s.notes}
            for s in sources
        ],
    }

@router.patch("/capital/{source_key}", summary="Update capital source progress")
async def update_capital(source_key: str, payload: CapitalUpdate, db: AsyncSession = Depends(get_db)) -> dict:
    try:
        source_enum = CapitalSource(source_key)
    except ValueError:
        raise HTTPException(400, f"Invalid source. Valid: {[s.value for s in CapitalSource]}")
    result = await db.execute(select(SkillShotCapital).where(SkillShotCapital.source == source_enum))
    cap = result.scalar_one_or_none()
    if not cap:
        raise HTTPException(404, "Capital source not found")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(cap, k, v)
    await db.commit()
    return {"message": "Capital source updated"}

# ── KPIs ──────────────────────────────────────────────────────────────────────

@router.get("/overview", summary="Skill Shot Academy KPI overview")
async def ss_overview(db: AsyncSession = Depends(get_db)) -> dict:
    bays_result = await db.execute(select(SkillShotBay))
    bays = bays_result.scalars().all()
    operational = sum(1 for b in bays if b.status == BayStatus.OPERATIONAL)

    sessions_result = await db.execute(select(SkillShotSession))
    sessions = sessions_result.scalars().all()
    total_revenue = sum(s.revenue for s in sessions)
    total_sessions = len(sessions)

    milestone_result = await db.execute(select(SkillShotMilestone))
    milestones = milestone_result.scalars().all()
    completed_m = sum(1 for m in milestones if m.status == MilestoneStatus.COMPLETED)
    at_risk_m   = sum(1 for m in milestones if m.status == MilestoneStatus.AT_RISK)
    blocked_m   = sum(1 for m in milestones if m.status == MilestoneStatus.BLOCKED)

    cap = await capital_stack(db)

    # Launch readiness score (0–100)
    readiness_components = {
        "bays_operational": min(operational / TRACKMAN_BAYS * 30, 30),       # 30 pts
        "capital_committed": min(cap["committed_pct"] / 100 * 25, 25),       # 25 pts
        "milestones_complete": min(completed_m / len(milestones) * 25, 25),  # 25 pts
        "revenue_generating": min(total_revenue / YEAR1_REVENUE_TARGET * 20, 20), # 20 pts
    }
    readiness_score = round(sum(readiness_components.values()))

    return {
        "bays_total": TRACKMAN_BAYS,
        "bays_operational": operational,
        "bays_in_progress": sum(1 for b in bays if b.status in [BayStatus.INSTALLATION, BayStatus.CALIBRATION]),
        "total_sessions": total_sessions,
        "total_revenue": round(total_revenue, 2),
        "year1_revenue_target": YEAR1_REVENUE_TARGET,
        "revenue_pacing_pct": round(total_revenue / YEAR1_REVENUE_TARGET * 100, 2),
        "milestones_total": len(milestones),
        "milestones_completed": completed_m,
        "milestones_at_risk": at_risk_m,
        "milestones_blocked": blocked_m,
        "capital_committed_pct": cap["committed_pct"],
        "capital_gap": cap["gap_to_close"],
        "launch_readiness_score": readiness_score,
        "readiness_breakdown": readiness_components,
        "investment_total": TOTAL_INVESTMENT,
    }

# ── AI Endpoints ──────────────────────────────────────────────────────────────

@router.post("/ai-launch-brief", summary="AI launch readiness and strategic action brief")
async def ai_launch_brief(db: AsyncSession = Depends(get_db)) -> dict:
    overview = await ss_overview(db)
    cap = await capital_stack(db)

    milestones_result = await db.execute(select(SkillShotMilestone).order_by(SkillShotMilestone.phase, SkillShotMilestone.target_date))
    milestones = milestones_result.scalars().all()
    blocked = [m for m in milestones if m.status in [MilestoneStatus.AT_RISK, MilestoneStatus.BLOCKED]]
    upcoming = [m for m in milestones if m.status == MilestoneStatus.NOT_STARTED and m.target_date and (m.target_date - date.today()).days <= 60]

    prompt = f"""
Skill Shot Academy — Launch Readiness Brief

CURRENT STATE:
- Launch Readiness Score: {overview['launch_readiness_score']}/100
- Bays operational: {overview['bays_operational']}/{overview['bays_total']}
- Bays in installation/calibration: {overview['bays_in_progress']}
- Sessions booked: {overview['total_sessions']}
- Revenue generated: ${overview['total_revenue']:,.0f} / ${overview['year1_revenue_target']:,.0f} target ({overview['revenue_pacing_pct']:.1f}%)

CAPITAL STACK (${overview['investment_total']:,.0f} total):
{chr(10).join(f"  {s['label']}: ${s['committed_amount']:,.0f} / ${s['target_amount']:,.0f} ({s['committed_pct']}%) — {s['status']}" for s in cap['sources'])}
Gap to close: ${cap['gap_to_close']:,.0f}

MILESTONE STATUS:
- Completed: {overview['milestones_completed']}/{overview['milestones_total']}
- At risk / blocked: {overview['milestones_at_risk'] + overview['milestones_blocked']}

Blockers/at-risk milestones:
{chr(10).join(f"  [{m.status}] {m.title} — {m.blockers or 'No details'}" for m in blocked)}

Upcoming in 60 days:
{chr(10).join(f"  {m.title} (Phase {m.phase}, due {m.target_date})" for m in upcoming[:6])}

Generate a 3-paragraph investor-quality launch brief:
1. Launch readiness assessment — honest evaluation of where the academy stands, what's working, what's behind schedule
2. Critical path — the 3 actions that most need to happen in the next 60 days to stay on track for Grand Opening
3. Revenue ramp projection — how to reach the $3.8M Year 1 target given current bay rollout pace, recommended session mix, and key corporate/league partnerships to close
"""

    response = claude.messages.create(
        model="claude-opus-4-5",
        max_tokens=700,
        system=SS_CONTEXT,
        messages=[{"role": "user", "content": prompt}],
    )

    return {
        "brief": response.content[0].text,
        "readiness_score": overview["launch_readiness_score"],
        "overview": overview,
        "generated_at": datetime.utcnow().isoformat(),
    }

@router.post("/ai-investor-brief", summary="AI investor-facing Skill Shot Academy narrative")
async def ai_investor_brief(db: AsyncSession = Depends(get_db)) -> dict:
    overview = await ss_overview(db)
    cap = await capital_stack(db)

    prompt = f"""
Generate a compelling investor narrative for Skill Shot Academy at NXS National Complex, Proctor MN.

FINANCIALS:
- Total investment: $4,650,000
- Year 1 revenue target: $3,800,000
- Capital committed: {cap['committed_pct']}% (${cap['total_committed']:,.0f})
- Bays operational: {overview['bays_operational']}/10

Write a 4-paragraph investor narrative:
1. The opportunity — golf/sports simulation market, Duluth-Superior region demand, why NXS is the right platform
2. The product — 10 TrackMan bays, session types (individual, lessons, leagues, corporate, simulator), pricing model (${BAY_RATE[SessionType.INDIVIDUAL]}–${BAY_RATE[SessionType.LESSON]}/hr)
3. The financial case — $3.8M Year 1, capital stack structure, path to profitability, scalability to additional markets
4. Why now — PuttView AR exclusive (within 200 miles), NXS campus ecosystem advantage, regional sports tourism momentum
"""

    response = claude.messages.create(
        model="claude-opus-4-5",
        max_tokens=700,
        system=SS_CONTEXT,
        messages=[{"role": "user", "content": prompt}],
    )

    return {
        "narrative": response.content[0].text,
        "generated_at": datetime.utcnow().isoformat(),
    }
