"""
SportAI Suite — Grant Tracker Router
Sprint 2 · Level Playing Field Foundation
IRRRB · MN DEED · LCCMR · GMRPTC — Application pipeline, award tracking,
compliance reporting, and AI narrative generation per funder

Add to main.py:
    from routers.grant_tracker import router as grant_router
    app.include_router(grant_router)
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

class Funder(str, enum.Enum):
    IRRRB    = "irrrb"    # Iron Range Resources & Rehabilitation Board
    MN_DEED  = "mn_deed"  # MN Dept of Employment & Economic Development
    LCCMR    = "lccmr"    # Legislative-Citizen Commission on MN Resources
    GMRPTC   = "gmrptc"   # Greater MN Regional Parks & Trails Commission
    NORTHLAND = "northland_foundation"
    DULUTH_COMMUNITY = "duluth_community_foundation"
    FEDERAL  = "federal"
    PRIVATE  = "private"
    OTHER    = "other"

class ApplicationStatus(str, enum.Enum):
    DRAFTING       = "drafting"
    SUBMITTED      = "submitted"
    UNDER_REVIEW   = "under_review"
    AWARDED        = "awarded"
    DECLINED       = "declined"
    WAITLISTED     = "waitlisted"
    WITHDRAWN      = "withdrawn"

class ComplianceStatus(str, enum.Enum):
    CURRENT    = "current"
    DUE_SOON   = "due_soon"
    OVERDUE    = "overdue"
    SUBMITTED  = "submitted"
    APPROVED   = "approved"

class GrantCategory(str, enum.Enum):
    CAPITAL       = "capital"         # Infrastructure / facility
    PROGRAMMING   = "programming"     # Youth programs / operations
    EQUIPMENT     = "equipment"       # Equipment purchase
    WORKFORCE     = "workforce"       # Jobs / economic development
    CONSERVATION  = "conservation"    # Environmental / natural resources
    TOURISM       = "tourism"         # Visitor / regional tourism
    TECHNOLOGY    = "technology"      # Tech / innovation
    GENERAL       = "general_operating"

# ── Funder profiles ───────────────────────────────────────────────────────────

FUNDER_PROFILES = {
    Funder.IRRRB: {
        "full_name": "Iron Range Resources & Rehabilitation Board",
        "focus": "Economic development, job creation, and community revitalization in Northeast Minnesota Iron Range region",
        "typical_range": "$50,000 – $500,000",
        "key_priorities": ["Job creation", "Economic diversification", "Tourism", "Infrastructure", "Youth development"],
        "alignment": "NXS creates 75+ jobs, drives regional tourism, and anchors economic development in Proctor/Duluth corridor",
        "contact": "irrrb.org",
        "deadline_typical": "Rolling + annual cycle",
    },
    Funder.MN_DEED: {
        "full_name": "MN Department of Employment & Economic Development",
        "focus": "Business development, workforce training, and economic development across Minnesota",
        "typical_range": "$25,000 – $1,000,000",
        "key_priorities": ["Job creation", "Workforce development", "Business expansion", "Greater MN investment"],
        "alignment": "NGP Development capital investment, NXS employment pipeline, regional economic anchor",
        "contact": "mn.gov/deed",
        "deadline_typical": "Quarterly cycles",
    },
    Funder.LCCMR: {
        "full_name": "Legislative-Citizen Commission on Minnesota Resources",
        "focus": "Natural resources conservation, outdoor recreation, and environmental stewardship",
        "typical_range": "$50,000 – $2,000,000",
        "key_priorities": ["Outdoor recreation access", "Conservation", "Trail connectivity", "Environmental education"],
        "alignment": "Trail connections to Superior Hiking Trail, Munger State Trail, Carlton Co. snowmobile corridor; outdoor sports access for youth",
        "contact": "lccmr.mn.gov",
        "deadline_typical": "Annual — January/February submission",
    },
    Funder.GMRPTC: {
        "full_name": "Greater Minnesota Regional Parks & Trails Commission",
        "focus": "Regional parks and trails infrastructure investment in Greater Minnesota",
        "typical_range": "$25,000 – $500,000",
        "key_priorities": ["Trail development", "Parks access", "Regional recreation", "Tourism infrastructure"],
        "alignment": "NXS campus trail connections, outdoor sports fields, campground, regional tourism draw",
        "contact": "gmrptc.org",
        "deadline_typical": "Annual — spring cycle",
    },
    Funder.NORTHLAND: {
        "full_name": "Northland Foundation",
        "focus": "Strengthening communities in northeastern Minnesota through philanthropy",
        "typical_range": "$5,000 – $100,000",
        "key_priorities": ["Youth development", "Community well-being", "Economic vitality", "Arts & culture"],
        "alignment": "LPF mission, youth sports access, Equipment Exchange, scholarship programs",
        "contact": "northlandfdn.org",
        "deadline_typical": "Quarterly",
    },
    Funder.DULUTH_COMMUNITY: {
        "full_name": "Duluth Community Foundation",
        "focus": "Improving quality of life in the greater Duluth community",
        "typical_range": "$5,000 – $75,000",
        "key_priorities": ["Youth programs", "Community development", "Health & wellness", "Education"],
        "alignment": "LPF programs, youth NIL, equipment access, Foundation Card scholarship hours",
        "contact": "duluthcommunityfoundation.org",
        "deadline_typical": "Semi-annual",
    },
}

# ── ORM Models ────────────────────────────────────────────────────────────────

class GrantFunder(Base):
    """Reference record for each grant funding organization."""
    __tablename__ = "grant_funders"

    id: Mapped[str]              = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    funder: Mapped[str]          = mapped_column(SAEnum(Funder), nullable=False, unique=True)
    full_name: Mapped[str]       = mapped_column(String(300), nullable=False)
    focus: Mapped[str]           = mapped_column(Text, nullable=True)
    typical_range: Mapped[str]   = mapped_column(String(100), nullable=True)
    contact_url: Mapped[str]     = mapped_column(String(300), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_priority: Mapped[bool]    = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    applications: Mapped[list["GrantApplication"]] = relationship("GrantApplication", back_populates="funder_ref")

class GrantApplication(Base):
    """Grant application — tracks full lifecycle from draft to award."""
    __tablename__ = "grant_applications"

    id: Mapped[str]               = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    funder_id: Mapped[str]        = mapped_column(ForeignKey("grant_funders.id"), nullable=False)
    funder: Mapped[str]           = mapped_column(SAEnum(Funder), nullable=False)
    title: Mapped[str]            = mapped_column(String(300), nullable=False)
    category: Mapped[str]         = mapped_column(SAEnum(GrantCategory), nullable=False)
    amount_requested: Mapped[float]       = mapped_column(Float, nullable=False)
    amount_awarded: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    status: Mapped[str]           = mapped_column(SAEnum(ApplicationStatus), default=ApplicationStatus.DRAFTING)
    submission_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    decision_date: Mapped[Optional[date]]   = mapped_column(Date, nullable=True)
    deadline: Mapped[Optional[date]]        = mapped_column(Date, nullable=True)
    grant_period_start: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    grant_period_end: Mapped[Optional[date]]   = mapped_column(Date, nullable=True)
    narrative: Mapped[Optional[str]]        = mapped_column(Text, nullable=True)   # AI-generated or manual
    lead_contact: Mapped[Optional[str]]     = mapped_column(String(200), nullable=True)
    notes: Mapped[Optional[str]]            = mapped_column(Text, nullable=True)
    is_active: Mapped[bool]                 = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime]            = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime]            = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    funder_ref: Mapped["GrantFunder"] = relationship("GrantFunder", back_populates="applications")
    compliance_events: Mapped[list["GrantComplianceEvent"]] = relationship("GrantComplianceEvent", back_populates="application", cascade="all, delete-orphan")

    @property
    def days_until_deadline(self) -> Optional[int]:
        if not self.deadline:
            return None
        return (self.deadline - date.today()).days

    @property
    def is_deadline_urgent(self) -> bool:
        d = self.days_until_deadline
        return d is not None and 0 <= d <= 30

class GrantComplianceEvent(Base):
    """Progress reports, site visits, financial reports — post-award compliance."""
    __tablename__ = "grant_compliance_events"

    id: Mapped[str]              = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    application_id: Mapped[str]  = mapped_column(ForeignKey("grant_applications.id"), nullable=False)
    event_type: Mapped[str]      = mapped_column(String(100), nullable=False)  # "progress_report", "site_visit", "financial_report"
    status: Mapped[str]          = mapped_column(SAEnum(ComplianceStatus), nullable=False)
    due_date: Mapped[Optional[date]]      = mapped_column(Date, nullable=True)
    submitted_date: Mapped[Optional[date]]= mapped_column(Date, nullable=True)
    notes: Mapped[Optional[str]]          = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime]          = mapped_column(DateTime(timezone=True), server_default=func.now())

    application: Mapped["GrantApplication"] = relationship("GrantApplication", back_populates="compliance_events")

# ── Pydantic ──────────────────────────────────────────────────────────────────

class ApplicationCreate(BaseModel):
    funder: Funder
    title: str
    category: GrantCategory
    amount_requested: float
    deadline: Optional[date] = None
    lead_contact: Optional[str] = None
    notes: Optional[str] = None

class ApplicationUpdate(BaseModel):
    status: Optional[ApplicationStatus] = None
    amount_awarded: Optional[float] = None
    decision_date: Optional[date] = None
    grant_period_start: Optional[date] = None
    grant_period_end: Optional[date] = None
    narrative: Optional[str] = None
    notes: Optional[str] = None

class ComplianceCreate(BaseModel):
    application_id: str
    event_type: str
    status: ComplianceStatus
    due_date: Optional[date] = None
    notes: Optional[str] = None

# ── DB dependency ─────────────────────────────────────────────────────────────

# ── Router ────────────────────────────────────────────────────────────────────

router = APIRouter(prefix="/api/grants", tags=["Grant Tracker"])
claude = Anthropic()

GRANT_CONTEXT = """
You are a grant writing and strategy expert for the Level Playing Field Foundation (LPF),
a 501(c)(3) nonprofit based in Proctor, MN. Executive Director: Shaun Marline.
Mission: Every Kid. Every Sport. Every Opportunity. #TimeToLevelUP
Website: levelplayingfieldfoundation.org

NXS National Complex — 704 Kirkus St, Proctor MN 55810 (ISG Project #24688001):
- Large Dome: 171,700 sqft | Smaller Dome: 36,100 sqft | Health Center: 15,700 sqft
- 2 outdoor soccer fields (195'×330') | Ice Rink (200'×85') | Campground
- 85-unit hotel | 40-unit apartments | 1,656 parking stalls
- Trail connections: Superior Hiking Trail, Willard Munger State Trail, Carlton Co. snowmobile corridor
- Phase 1: $1.847M/yr revenue | Phase 2: Skill Shot Academy ($4.65M), PuttView AR Exclusive
- 5-year combined: $35.6M | IRR 36.8% | Payback 3.1 years | Capital pipeline: $9.85M

LPF Programs: Equipment Exchange (100+ drop boxes), Scholarships ($300/$500/$750+),
NIL Program (50+ HS athletes), Replay Sports Store, Foundation Card (1,350→4,500 members).
8 sports: flag football, soccer, lacrosse, volleyball, softball, basketball, pickleball, robotics.

Problem: 70% of youth quit sports by age 13. Cost is the #1 barrier.
No comparable organization within 60 miles.

Generate compelling, specific, funder-aligned grant narratives.
"""

# ── Seed ──────────────────────────────────────────────────────────────────────

@router.post("/seed", summary="Seed grant funders and sample applications")
async def seed_grants(db: AsyncSession = Depends(get_db)) -> dict:
    existing = await db.scalar(select(func.count()).select_from(GrantFunder))
    if existing and existing > 0:
        return {"message": f"Already seeded — {existing} funders exist", "seeded": False}

    today = date.today()

    # Seed funders
    funder_records = {}
    for funder_enum, profile in FUNDER_PROFILES.items():
        f = GrantFunder(
            funder=funder_enum,
            full_name=profile["full_name"],
            focus=profile["focus"],
            typical_range=profile["typical_range"],
            contact_url=profile["contact"],
            is_priority=funder_enum in [Funder.IRRRB, Funder.MN_DEED, Funder.LCCMR, Funder.GMRPTC],
        )
        db.add(f)
        funder_records[funder_enum] = f

    await db.flush()

    # Seed applications across the pipeline
    apps_data = [
        {
            "funder": Funder.IRRRB, "funder_id": funder_records[Funder.IRRRB].id,
            "title": "NXS National Complex Phase 2 — Economic Development Capital Grant",
            "category": GrantCategory.CAPITAL, "amount_requested": 500_000.0,
            "status": ApplicationStatus.SUBMITTED,
            "submission_date": today - timedelta(days=45),
            "deadline": today + timedelta(days=60),
            "lead_contact": "Shaun Marline — shaun.marline@gmail.com",
        },
        {
            "funder": Funder.MN_DEED, "funder_id": funder_records[Funder.MN_DEED].id,
            "title": "NXS Workforce Development & Youth Employment Initiative",
            "category": GrantCategory.WORKFORCE, "amount_requested": 250_000.0,
            "status": ApplicationStatus.UNDER_REVIEW,
            "submission_date": today - timedelta(days=90),
            "deadline": today + timedelta(days=30),
            "lead_contact": "Shaun Marline — shaun.marline@gmail.com",
        },
        {
            "funder": Funder.LCCMR, "funder_id": funder_records[Funder.LCCMR].id,
            "title": "Greater MN Outdoor Recreation Access — Trail-Connected Sports Campus",
            "category": GrantCategory.CONSERVATION, "amount_requested": 350_000.0,
            "status": ApplicationStatus.DRAFTING,
            "deadline": today + timedelta(days=90),
            "lead_contact": "Shaun Marline — shaun.marline@gmail.com",
        },
        {
            "funder": Funder.GMRPTC, "funder_id": funder_records[Funder.GMRPTC].id,
            "title": "Proctor MN Regional Trails & Sports Facility Connector Grant",
            "category": GrantCategory.TOURISM, "amount_requested": 150_000.0,
            "status": ApplicationStatus.AWARDED,
            "submission_date": today - timedelta(days=180),
            "decision_date": today - timedelta(days=30),
            "amount_awarded": 120_000.0,
            "grant_period_start": today - timedelta(days=30),
            "grant_period_end": today + timedelta(days=335),
        },
        {
            "funder": Funder.NORTHLAND, "funder_id": funder_records[Funder.NORTHLAND].id,
            "title": "Level Playing Field Foundation — Youth Equipment Access Program",
            "category": GrantCategory.PROGRAMMING, "amount_requested": 50_000.0,
            "status": ApplicationStatus.AWARDED,
            "submission_date": today - timedelta(days=200),
            "decision_date": today - timedelta(days=60),
            "amount_awarded": 40_000.0,
            "grant_period_start": today - timedelta(days=60),
            "grant_period_end": today + timedelta(days=305),
        },
        {
            "funder": Funder.DULUTH_COMMUNITY, "funder_id": funder_records[Funder.DULUTH_COMMUNITY].id,
            "title": "LPF Scholarship Fund — Duluth Youth Sports Access",
            "category": GrantCategory.PROGRAMMING, "amount_requested": 25_000.0,
            "status": ApplicationStatus.DECLINED,
            "submission_date": today - timedelta(days=120),
            "decision_date": today - timedelta(days=30),
        },
        {
            "funder": Funder.IRRRB, "funder_id": funder_records[Funder.IRRRB].id,
            "title": "PuttView AR Exclusive License — Regional Tourism Tech Investment",
            "category": GrantCategory.TOURISM, "amount_requested": 200_000.0,
            "status": ApplicationStatus.DRAFTING,
            "deadline": today + timedelta(days=120),
        },
    ]

    created_apps = []
    for a_data in apps_data:
        app = GrantApplication(**a_data)
        db.add(app)
        created_apps.append(app)

    await db.flush()

    # Seed compliance events for awarded grants
    awarded_apps = [a for a in created_apps if a.status == ApplicationStatus.AWARDED]
    for app in awarded_apps:
        events = [
            GrantComplianceEvent(application_id=app.id, event_type="initial_progress_report",
                                  status=ComplianceStatus.SUBMITTED, due_date=app.grant_period_start + timedelta(days=90) if app.grant_period_start else None,
                                  submitted_date=app.grant_period_start + timedelta(days=85) if app.grant_period_start else None),
            GrantComplianceEvent(application_id=app.id, event_type="mid_term_financial_report",
                                  status=ComplianceStatus.DUE_SOON, due_date=date.today() + timedelta(days=25),
                                  notes="Quarterly financial report + youth served count required"),
            GrantComplianceEvent(application_id=app.id, event_type="final_report",
                                  status=ComplianceStatus.CURRENT, due_date=app.grant_period_end if app.grant_period_end else None),
        ]
        for e in events:
            db.add(e)

    await db.commit()
    return {
        "message": "Grant Tracker seeded",
        "funders": len(FUNDER_PROFILES),
        "applications": len(apps_data),
        "seeded": True,
    }

# ── Funders ───────────────────────────────────────────────────────────────────

@router.get("/funders", summary="List all grant funders with profiles")
async def list_funders(priority_only: bool = Query(False), db: AsyncSession = Depends(get_db)) -> list[dict]:
    q = select(GrantFunder)
    if priority_only:
        q = q.where(GrantFunder.is_priority == True)
    result = await db.execute(q)
    funders = result.scalars().all()
    return [
        {
            "id": f.id, "funder": f.funder, "full_name": f.full_name,
            "focus": f.focus, "typical_range": f.typical_range,
            "contact_url": f.contact_url, "is_priority": f.is_priority,
            "profile": FUNDER_PROFILES.get(f.funder, {}),
        }
        for f in funders
    ]

# ── Applications ──────────────────────────────────────────────────────────────

@router.get("/applications", summary="List applications with optional filters")
async def list_applications(
    funder: Optional[Funder] = Query(None),
    status: Optional[ApplicationStatus] = Query(None),
    category: Optional[GrantCategory] = Query(None),
    urgent_only: bool = Query(False),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    q = select(GrantApplication).where(GrantApplication.is_active == True)
    if funder:   q = q.where(GrantApplication.funder == funder)
    if status:   q = q.where(GrantApplication.status == status)
    if category: q = q.where(GrantApplication.category == category)

    result = await db.execute(q)
    apps = result.scalars().all()
    if urgent_only:
        apps = [a for a in apps if a.is_deadline_urgent]

    return [
        {
            "id": a.id, "funder": a.funder, "title": a.title,
            "category": a.category, "amount_requested": a.amount_requested,
            "amount_awarded": a.amount_awarded, "status": a.status,
            "submission_date": a.submission_date.isoformat() if a.submission_date else None,
            "decision_date": a.decision_date.isoformat() if a.decision_date else None,
            "deadline": a.deadline.isoformat() if a.deadline else None,
            "days_until_deadline": a.days_until_deadline,
            "is_deadline_urgent": a.is_deadline_urgent,
            "lead_contact": a.lead_contact,
        }
        for a in apps
    ]

@router.post("/applications", summary="Create a new grant application")
async def create_application(payload: ApplicationCreate, db: AsyncSession = Depends(get_db)) -> dict:
    # Get or create funder record
    funder_result = await db.execute(select(GrantFunder).where(GrantFunder.funder == payload.funder))
    funder_rec = funder_result.scalar_one_or_none()
    if not funder_rec:
        raise HTTPException(404, f"Funder {payload.funder} not found — run /api/grants/seed first")

    app = GrantApplication(**payload.model_dump(), funder_id=funder_rec.id)
    db.add(app)
    await db.commit()
    await db.refresh(app)
    return {"id": app.id, "title": app.title, "message": "Application created"}

@router.patch("/applications/{app_id}", summary="Update application status or award")
async def update_application(app_id: str, payload: ApplicationUpdate, db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(select(GrantApplication).where(GrantApplication.id == app_id))
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(404, "Application not found")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(app, k, v)
    await db.commit()
    return {"id": app.id, "message": "Application updated"}

# ── Compliance ────────────────────────────────────────────────────────────────

@router.get("/compliance", summary="Open compliance events across all awarded grants")
async def compliance_overview(db: AsyncSession = Depends(get_db)) -> dict:
    q = select(GrantComplianceEvent).where(
        GrantComplianceEvent.status.in_([ComplianceStatus.DUE_SOON, ComplianceStatus.OVERDUE])
    )
    result = await db.execute(q)
    events = result.scalars().all()

    overdue   = [e for e in events if e.status == ComplianceStatus.OVERDUE]
    due_soon  = [e for e in events if e.status == ComplianceStatus.DUE_SOON]

    return {
        "overdue": [{"id": e.id, "application_id": e.application_id, "event_type": e.event_type,
                     "due_date": e.due_date.isoformat() if e.due_date else None, "notes": e.notes} for e in overdue],
        "due_soon": [{"id": e.id, "application_id": e.application_id, "event_type": e.event_type,
                      "due_date": e.due_date.isoformat() if e.due_date else None,
                      "days_until_due": (e.due_date - date.today()).days if e.due_date else None} for e in due_soon],
        "summary": {"overdue_count": len(overdue), "due_soon_count": len(due_soon)},
    }

@router.post("/compliance", summary="Log a compliance event")
async def log_compliance(payload: ComplianceCreate, db: AsyncSession = Depends(get_db)) -> dict:
    event = GrantComplianceEvent(**payload.model_dump())
    db.add(event)
    await db.commit()
    return {"message": "Compliance event logged"}

# ── KPIs ──────────────────────────────────────────────────────────────────────

@router.get("/kpis", summary="Grant program KPI snapshot")
async def grant_kpis(db: AsyncSession = Depends(get_db)) -> dict:
    apps_result = await db.execute(select(GrantApplication).where(GrantApplication.is_active == True))
    apps = apps_result.scalars().all()

    total_requested = sum(a.amount_requested for a in apps)
    total_awarded   = sum(a.amount_awarded or 0 for a in apps if a.status == ApplicationStatus.AWARDED)
    in_pipeline     = sum(a.amount_requested for a in apps if a.status in [ApplicationStatus.SUBMITTED, ApplicationStatus.UNDER_REVIEW])
    drafting        = sum(1 for a in apps if a.status == ApplicationStatus.DRAFTING)
    awarded_count   = sum(1 for a in apps if a.status == ApplicationStatus.AWARDED)
    declined_count  = sum(1 for a in apps if a.status == ApplicationStatus.DECLINED)
    urgent          = sum(1 for a in apps if a.is_deadline_urgent)

    status_breakdown = {}
    for a in apps:
        status_breakdown[a.status] = status_breakdown.get(a.status, 0) + 1

    funder_breakdown = {}
    for a in apps:
        if a.funder not in funder_breakdown:
            funder_breakdown[a.funder] = {"applications": 0, "requested": 0, "awarded": 0}
        funder_breakdown[a.funder]["applications"] += 1
        funder_breakdown[a.funder]["requested"] += a.amount_requested
        if a.status == ApplicationStatus.AWARDED:
            funder_breakdown[a.funder]["awarded"] += a.amount_awarded or 0

    win_rate = round(awarded_count / (awarded_count + declined_count) * 100, 1) if (awarded_count + declined_count) > 0 else 0

    return {
        "total_applications": len(apps),
        "total_requested": round(total_requested, 2),
        "total_awarded": round(total_awarded, 2),
        "in_pipeline": round(in_pipeline, 2),
        "drafting_count": drafting,
        "awarded_count": awarded_count,
        "declined_count": declined_count,
        "win_rate_pct": win_rate,
        "urgent_deadlines": urgent,
        "status_breakdown": status_breakdown,
        "funder_breakdown": {k: {kk: round(vv, 2) if isinstance(vv, float) else vv for kk, vv in v.items()} for k, v in funder_breakdown.items()},
    }

# ── AI Narrative Generation ───────────────────────────────────────────────────

@router.post("/ai-narrative/{funder_key}", summary="Generate AI grant narrative for specific funder")
async def ai_narrative(
    funder_key: str,
    amount: float = Query(250_000.0, description="Grant amount to request"),
    category: GrantCategory = Query(GrantCategory.CAPITAL),
    db: AsyncSession = Depends(get_db),
) -> dict:
    try:
        funder_enum = Funder(funder_key)
    except ValueError:
        raise HTTPException(400, f"Unknown funder key. Valid: {[f.value for f in Funder]}")

    profile = FUNDER_PROFILES.get(funder_enum)
    if not profile:
        raise HTTPException(400, f"No profile found for funder {funder_key}")

    prompt = f"""
Generate a compelling grant narrative for the following:

FUNDER: {profile['full_name']}
FUNDER FOCUS: {profile['focus']}
FUNDER PRIORITIES: {', '.join(profile.get('key_priorities', []))}
LPF ALIGNMENT: {profile['alignment']}
AMOUNT REQUESTED: ${amount:,.0f}
GRANT CATEGORY: {category.value}

Write a professional grant narrative with these 5 sections:

1. EXECUTIVE SUMMARY (2 paragraphs)
   - Opening hook aligned to funder's mission
   - Project overview and ask

2. STATEMENT OF NEED (2 paragraphs)
   - The problem: 70% youth quit sports by 13, cost #1 barrier, no comparable org within 60 miles
   - Community need data for Northeast MN / Iron Range / Proctor-Duluth corridor

3. PROJECT DESCRIPTION (3 paragraphs)
   - NXS National Complex specifics (facility, capacity, sports, programs)
   - LPF programs (Equipment Exchange, Scholarships, NIL, Foundation Card, Replay Store)
   - Phase 2 vision (Skill Shot Academy, PuttView AR, hotel, restaurant)

4. OUTCOMES & IMPACT (1 paragraph)
   - Quantified: youth served, jobs created, economic impact, tourism draw, revenue targets
   - Align metrics to {profile['full_name']}'s reporting requirements

5. ORGANIZATIONAL CAPACITY (1 paragraph)
   - Shaun Marline's leadership, board governance, $35.6M 5-year track record
   - Existing partnerships and community trust

Format each section with the section header in ALL CAPS, then the narrative text.
Be specific, compelling, and funder-aligned throughout. Avoid generic language.
"""

    response = claude.messages.create(
        model="claude-opus-4-5",
        max_tokens=1500,
        system=GRANT_CONTEXT,
        messages=[{"role": "user", "content": prompt}],
    )

    return {
        "funder": funder_enum,
        "funder_name": profile["full_name"],
        "amount_requested": amount,
        "category": category,
        "narrative": response.content[0].text,
        "profile": profile,
        "generated_at": datetime.utcnow().isoformat(),
    }

@router.post("/ai-pipeline-brief", summary="AI grant pipeline strategy brief")
async def ai_pipeline_brief(db: AsyncSession = Depends(get_db)) -> dict:
    kpis = await grant_kpis(db)
    compliance = await compliance_overview(db)

    prompt = f"""
LPF Grant Program — Strategic Pipeline Brief

Pipeline snapshot:
- Total applications: {kpis['total_applications']}
- Total requested: ${kpis['total_requested']:,.0f}
- Total awarded: ${kpis['total_awarded']:,.0f}
- In active pipeline: ${kpis['in_pipeline']:,.0f}
- Win rate: {kpis['win_rate_pct']}%
- Urgent deadlines: {kpis['urgent_deadlines']}
- Drafting: {kpis['drafting_count']} applications

By funder:
{chr(10).join(f"  {k}: {v['applications']} apps | ${v['requested']:,.0f} requested | ${v['awarded']:,.0f} awarded" for k, v in kpis['funder_breakdown'].items())}

Compliance:
- Overdue reports: {compliance['summary']['overdue_count']}
- Due soon: {compliance['summary']['due_soon_count']}

Generate a 3-paragraph strategic brief:
1. Portfolio health — win rate assessment, pipeline strength, funder relationship status
2. Immediate actions — which applications need attention this week (deadlines, compliance, narrative polish)
3. 90-day grant strategy — which funders to prioritize next, what amounts to target, and how to use awarded grants as proof points for future applications
"""

    response = claude.messages.create(
        model="claude-opus-4-5",
        max_tokens=650,
        system=GRANT_CONTEXT,
        messages=[{"role": "user", "content": prompt}],
    )

    return {
        "brief": response.content[0].text,
        "kpis": kpis,
        "generated_at": datetime.utcnow().isoformat(),
    }
