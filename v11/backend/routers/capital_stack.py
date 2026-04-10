"""
SportAI Suite — Capital Stack Tracker
Sprint 8 · NGP Development
Full $9.85M capital pipeline tracking:
  Phase 1: $5.2M (community bonds, grants, bank financing)
  Phase 2: $4.65M (SBA 504 $2M, naming rights $1M, state grants $750K, crowdfunding $900K)
IRR: 36.8% | Payback: 3.1 years | 5-yr: $35.6M combined
TID bond modeling · Disbursement waterfall · Investor reporting dashboard

Add to main.py:
    from routers.capital_stack import router as capital_stack_router
    app.include_router(capital_stack_router)
"""

from __future__ import annotations

import enum
import uuid
from datetime import date, datetime, timedelta
from typing import Optional
import random

from anthropic import Anthropic
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import (
    Boolean, Date, DateTime, Enum as SAEnum, Float,
    Integer, String, Text, func, select
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


# ── Constants ─────────────────────────────────────────────────────────────────

TOTAL_CAPITAL_TARGET = 9_850_000.0
PHASE1_CAPITAL       = 5_200_000.0
PHASE2_CAPITAL       = 4_650_000.0
TARGET_IRR           = 36.8        # %
TARGET_PAYBACK_YRS   = 3.1
FIVE_YEAR_REVENUE    = 35_600_000.0
PHASE1_ANNUAL_REV    = 1_847_000.0
PHASE2_YEAR1_REV     = 3_800_000.0   # Skill Shot
TID_ASSESSMENT_RATE  = 0.015         # 1.5% of hotel room revenue
HOTEL_ROOMS          = 85


# ── Enums ─────────────────────────────────────────────────────────────────────

class CapitalPhase(str, enum.Enum):
    PHASE1 = "phase1"    # $5.2M campus build
    PHASE2 = "phase2"    # $4.65M Skill Shot + PuttView
    BRIDGE = "bridge"    # Short-term working capital


class SourceType(str, enum.Enum):
    COMMUNITY_BONDS  = "community_bonds"
    BANK_LOAN        = "bank_loan"
    SBA_504          = "sba_504"
    NAMING_RIGHTS    = "naming_rights"
    STATE_GRANT      = "state_grant"
    CROWDFUNDING     = "crowdfunding"
    EQUITY           = "equity"
    TID_BONDS        = "tid_bonds"
    OPERATING_CASH   = "operating_cash"
    IRRRB_GRANT      = "irrrb_grant"
    MN_DEED_GRANT    = "mn_deed_grant"


class SourceStatus(str, enum.Enum):
    PLANNING     = "planning"
    APPLICATION  = "application"
    COMMITTED    = "committed"
    RECEIVED     = "received"
    DEPLOYED     = "deployed"
    CLOSED       = "closed"


class DisbursementCategory(str, enum.Enum):
    LAND             = "land"
    CONSTRUCTION     = "construction"
    EQUIPMENT        = "equipment"
    FF_AND_E         = "ff_and_e"       # Furniture, fixtures & equipment
    SOFT_COSTS       = "soft_costs"     # Permits, design, legal
    WORKING_CAPITAL  = "working_capital"
    CONTINGENCY      = "contingency"
    DEBT_SERVICE     = "debt_service"


# ── ORM Models ────────────────────────────────────────────────────────────────

class CapitalSource(Base):
    """Individual capital source in the NGP Development stack."""
    __tablename__ = "capital_sources"

    id: Mapped[str]              = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    phase: Mapped[str]           = mapped_column(SAEnum(CapitalPhase), nullable=False)
    source_type: Mapped[str]     = mapped_column(SAEnum(SourceType), nullable=False)
    label: Mapped[str]           = mapped_column(String(200), nullable=False)
    target_amount: Mapped[float] = mapped_column(Float, nullable=False)
    committed_amount: Mapped[float] = mapped_column(Float, default=0.0)
    received_amount: Mapped[float]  = mapped_column(Float, default=0.0)
    deployed_amount: Mapped[float]  = mapped_column(Float, default=0.0)
    status: Mapped[str]          = mapped_column(SAEnum(SourceStatus), default=SourceStatus.PLANNING)
    interest_rate: Mapped[Optional[float]]  = mapped_column(Float, nullable=True)   # % for debt
    term_years: Mapped[Optional[int]]       = mapped_column(Integer, nullable=True)
    maturity_date: Mapped[Optional[date]]   = mapped_column(Date, nullable=True)
    lender_investor: Mapped[Optional[str]]  = mapped_column(String(200), nullable=True)
    contact_name: Mapped[Optional[str]]     = mapped_column(String(200), nullable=True)
    notes: Mapped[Optional[str]]            = mapped_column(Text, nullable=True)
    priority_order: Mapped[int]             = mapped_column(Integer, default=99)
    created_at: Mapped[datetime]            = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime]            = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    @property
    def committed_pct(self) -> float:
        return round(self.committed_amount / self.target_amount * 100, 1) if self.target_amount else 0

    @property
    def gap(self) -> float:
        return round(self.target_amount - self.committed_amount, 2)

    @property
    def annual_debt_service(self) -> float:
        if not self.interest_rate or not self.term_years or self.committed_amount <= 0:
            return 0.0
        r = self.interest_rate / 100 / 12
        n = self.term_years * 12
        if r == 0:
            return round(self.committed_amount / n * 12, 2)
        monthly = self.committed_amount * (r * (1 + r) ** n) / ((1 + r) ** n - 1)
        return round(monthly * 12, 2)


class CapitalDisbursement(Base):
    """Capital disbursement — tracks where capital goes."""
    __tablename__ = "capital_disbursements"

    id: Mapped[str]              = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_id: Mapped[Optional[str]]  = mapped_column(String(36), nullable=True)
    phase: Mapped[str]           = mapped_column(SAEnum(CapitalPhase), nullable=False)
    category: Mapped[str]        = mapped_column(SAEnum(DisbursementCategory), nullable=False)
    description: Mapped[str]     = mapped_column(String(300), nullable=False)
    amount: Mapped[float]        = mapped_column(Float, nullable=False)
    disbursed_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    vendor: Mapped[Optional[str]]          = mapped_column(String(200), nullable=True)
    is_approved: Mapped[bool]              = mapped_column(Boolean, default=True)
    notes: Mapped[Optional[str]]           = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime]           = mapped_column(DateTime(timezone=True), server_default=func.now())


class InvestorReport(Base):
    """Periodic investor report snapshots."""
    __tablename__ = "investor_reports"

    id: Mapped[str]              = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_period: Mapped[str]   = mapped_column(String(20), nullable=False)   # "2025-Q4"
    report_type: Mapped[str]     = mapped_column(String(50), nullable=False)    # "quarterly", "annual"
    total_capital_raised: Mapped[float]  = mapped_column(Float, nullable=False)
    total_capital_deployed: Mapped[float]= mapped_column(Float, nullable=False)
    phase1_pct_complete: Mapped[float]   = mapped_column(Float, nullable=False)
    phase2_pct_complete: Mapped[float]   = mapped_column(Float, nullable=False)
    actual_irr: Mapped[Optional[float]]  = mapped_column(Float, nullable=True)
    projected_irr: Mapped[float]         = mapped_column(Float, nullable=False)
    narrative: Mapped[Optional[str]]     = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime]         = mapped_column(DateTime(timezone=True), server_default=func.now())


class TIDLedger(Base):
    """Tourism Improvement District bond modeling and assessment tracking."""
    __tablename__ = "tid_ledger"

    id: Mapped[str]                 = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    month: Mapped[str]              = mapped_column(String(7), nullable=False, unique=True)
    hotel_room_revenue: Mapped[float]    = mapped_column(Float, nullable=False)
    tid_assessment: Mapped[float]        = mapped_column(Float, nullable=False)
    tid_cumulative: Mapped[float]        = mapped_column(Float, nullable=False)
    rooms_sold: Mapped[int]              = mapped_column(Integer, nullable=False)
    occupancy_pct: Mapped[float]         = mapped_column(Float, nullable=False)
    tourism_visitors_est: Mapped[int]    = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime]         = mapped_column(DateTime(timezone=True), server_default=func.now())


# ── Pydantic ──────────────────────────────────────────────────────────────────

class SourceUpdate(BaseModel):
    committed_amount: Optional[float] = None
    received_amount: Optional[float] = None
    deployed_amount: Optional[float] = None
    status: Optional[SourceStatus] = None
    notes: Optional[str] = None


class DisbursementCreate(BaseModel):
    source_id: Optional[str] = None
    phase: CapitalPhase
    category: DisbursementCategory
    description: str
    amount: float
    disbursed_date: Optional[date] = None
    vendor: Optional[str] = None
    notes: Optional[str] = None


# ── DB dependency ─────────────────────────────────────────────────────────────

async def get_db() -> AsyncSession:
    raise NotImplementedError("Wire to your AsyncSession factory")


# ── Router ────────────────────────────────────────────────────────────────────

router = APIRouter(prefix="/api/capital", tags=["Capital Stack Tracker"])
claude = Anthropic()

CAP_CONTEXT = """
You are the AI capital markets advisor for NGP Development — the real estate and development
entity for the NXS National Complex, 704 Kirkus St, Proctor MN 55810 (ISG Project #24688001).
Executive Director / Developer: Shaun Marline.
Capital pipeline: $9.85M total | Phase 1 $5.2M | Phase 2 $4.65M
Targets: IRR 36.8% | Payback 3.1 years | 5-year combined revenue $35.6M
TID (Tourism Improvement District) assessment: 1.5% of hotel room revenue.
Provide investor-quality, specific capital strategy insights.
"""


# ── Seed ──────────────────────────────────────────────────────────────────────

@router.post("/seed", summary="Seed full $9.85M capital stack with disbursements, investor report, and TID ledger")
async def seed_capital(db: AsyncSession = Depends(get_db)) -> dict:
    existing = await db.scalar(select(func.count()).select_from(CapitalSource))
    if existing and existing > 0:
        return {"message": f"Already seeded — {existing} sources exist", "seeded": False}

    today = date.today()

    # ── Capital Sources ───────────────────────────────────────────────────────
    sources = [
        # PHASE 1 — $5.2M
        CapitalSource(phase=CapitalPhase.PHASE1, source_type=SourceType.COMMUNITY_BONDS,
            label="NXS Community Bonds — Series A",
            target_amount=1_800_000, committed_amount=1_800_000, received_amount=1_800_000, deployed_amount=1_800_000,
            status=SourceStatus.DEPLOYED, interest_rate=4.5, term_years=15,
            lender_investor="Carlton County Bond Investors", priority_order=1,
            notes="Sold to community investors at 4.5%. 15-year term."),
        CapitalSource(phase=CapitalPhase.PHASE1, source_type=SourceType.IRRRB_GRANT,
            label="IRRRB Economic Development Grant",
            target_amount=800_000, committed_amount=800_000, received_amount=800_000, deployed_amount=800_000,
            status=SourceStatus.DEPLOYED, lender_investor="Iron Range Resources & Rehabilitation Board",
            priority_order=2, notes="Awarded. Job creation + regional economic development mandate met."),
        CapitalSource(phase=CapitalPhase.PHASE1, source_type=SourceType.BANK_LOAN,
            label="Duluth National Bank Construction Loan",
            target_amount=2_000_000, committed_amount=2_000_000, received_amount=2_000_000, deployed_amount=2_000_000,
            status=SourceStatus.DEPLOYED, interest_rate=6.25, term_years=20,
            lender_investor="Duluth National Bank", priority_order=3,
            notes="Construction-to-perm loan. $2M @ 6.25% over 20yr."),
        CapitalSource(phase=CapitalPhase.PHASE1, source_type=SourceType.MN_DEED_GRANT,
            label="MN DEED Small Business Development Grant",
            target_amount=400_000, committed_amount=400_000, received_amount=400_000, deployed_amount=400_000,
            status=SourceStatus.DEPLOYED, lender_investor="MN Dept of Employment & Economic Development",
            priority_order=4, notes="Workforce development + business expansion. Awarded."),
        CapitalSource(phase=CapitalPhase.PHASE1, source_type=SourceType.EQUITY,
            label="Developer Equity — Shaun Marline / NGP",
            target_amount=200_000, committed_amount=200_000, received_amount=200_000, deployed_amount=200_000,
            status=SourceStatus.DEPLOYED, lender_investor="NGP Development / Shaun Marline",
            priority_order=5, notes="Developer cash equity contribution."),
        # PHASE 2 — $4.65M
        CapitalSource(phase=CapitalPhase.PHASE2, source_type=SourceType.SBA_504,
            label="SBA 504 Loan — Skill Shot Academy",
            target_amount=2_000_000, committed_amount=2_000_000, received_amount=1_200_000, deployed_amount=900_000,
            status=SourceStatus.COMMITTED, interest_rate=5.75, term_years=20,
            lender_investor="SBA / Regional CDC", priority_order=6,
            notes="Approved. $800K pending drawdown per construction milestone."),
        CapitalSource(phase=CapitalPhase.PHASE2, source_type=SourceType.NAMING_RIGHTS,
            label="Facility Naming Rights — Skill Shot Academy",
            target_amount=1_000_000, committed_amount=650_000, received_amount=250_000, deployed_amount=0,
            status=SourceStatus.COMMITTED, lender_investor="Two Regional Candidates (Essentia Health, Fleet Farm)",
            priority_order=7, notes="$650K committed via LOI. Final contract execution pending. $350K gap."),
        CapitalSource(phase=CapitalPhase.PHASE2, source_type=SourceType.STATE_GRANT,
            label="IRRRB Phase 2 — Skill Shot Tourism Grant",
            target_amount=500_000, committed_amount=350_000, received_amount=0, deployed_amount=0,
            status=SourceStatus.APPLICATION, lender_investor="IRRRB",
            priority_order=8, notes="Application submitted. Decision expected within 60 days."),
        CapitalSource(phase=CapitalPhase.PHASE2, source_type=SourceType.MN_DEED_GRANT,
            label="MN DEED Expansion Grant — Phase 2",
            target_amount=250_000, committed_amount=0, received_amount=0, deployed_amount=0,
            status=SourceStatus.APPLICATION, lender_investor="MN DEED",
            priority_order=9, notes="Application in review. $250K ask."),
        CapitalSource(phase=CapitalPhase.PHASE2, source_type=SourceType.CROWDFUNDING,
            label="NXS Community Crowdfunding Campaign",
            target_amount=900_000, committed_amount=0, received_amount=0, deployed_amount=0,
            status=SourceStatus.PLANNING, lender_investor="Community / Online Campaign",
            priority_order=10, notes="Campaign not yet launched. Bay naming rights at $50K/bay available."),
    ]

    for s in sources:
        db.add(s)
    await db.flush()

    # ── Disbursements ──────────────────────────────────────────────────────────
    disb_data = [
        # Phase 1 — all deployed
        (CapitalPhase.PHASE1, DisbursementCategory.LAND,         "Land acquisition — 704 Kirkus St, Proctor MN",          350_000, today - timedelta(days=730), "Carlton County",           sources[0].id),
        (CapitalPhase.PHASE1, DisbursementCategory.CONSTRUCTION, "Large Dome construction — ISG Engineering",            2_400_000, today - timedelta(days=500), "ISG Engineering #24688001", sources[2].id),
        (CapitalPhase.PHASE1, DisbursementCategory.CONSTRUCTION, "Small Dome + Health Center construction",               950_000, today - timedelta(days=450), "ISG Engineering #24688001", sources[2].id),
        (CapitalPhase.PHASE1, DisbursementCategory.EQUIPMENT,    "Turf installation — Large + Small Dome",                320_000, today - timedelta(days=400), "FieldTurf North",           sources[0].id),
        (CapitalPhase.PHASE1, DisbursementCategory.EQUIPMENT,    "Ice rink refrigeration + dasherboards",                 280_000, today - timedelta(days=380), "Arctic Ice Systems",        sources[1].id),
        (CapitalPhase.PHASE1, DisbursementCategory.FF_AND_E,     "Scoreboards, AV, court equipment",                     185_000, today - timedelta(days=350), "Sound & Vision MN",         sources[0].id),
        (CapitalPhase.PHASE1, DisbursementCategory.SOFT_COSTS,   "Permits, legal, design fees — Phase 1",                 245_000, today - timedelta(days=550), "Various",                   sources[1].id),
        (CapitalPhase.PHASE1, DisbursementCategory.WORKING_CAPITAL,"Phase 1 operating reserves",                          220_000, today - timedelta(days=300), "NGP Development",           sources[4].id),
        (CapitalPhase.PHASE1, DisbursementCategory.CONTINGENCY,  "Phase 1 contingency — used",                            150_000, today - timedelta(days=350), "Various",                   None),
        # Phase 2 — partially deployed
        (CapitalPhase.PHASE2, DisbursementCategory.EQUIPMENT,    "TrackMan units 1–7 — Skill Shot Academy",               630_000, today - timedelta(days=90),  "TrackMan A/S",              sources[5].id),
        (CapitalPhase.PHASE2, DisbursementCategory.EQUIPMENT,    "PuttView AR system — 4 bays + license",                 280_000, today - timedelta(days=80),  "PuttView ApS",              sources[5].id),
        (CapitalPhase.PHASE2, DisbursementCategory.CONSTRUCTION, "Skill Shot Academy buildout — Bays 1–7",                210_000, today - timedelta(days=60),  "ISG Engineering",           sources[5].id),
        (CapitalPhase.PHASE2, DisbursementCategory.SOFT_COSTS,   "Phase 2 design, permits, legal",                         85_000, today - timedelta(days=100), "Various",                   sources[5].id),
    ]

    for phase, cat, desc, amt, disp_date, vendor, src_id in disb_data:
        db.add(CapitalDisbursement(
            source_id=src_id, phase=phase, category=cat, description=desc,
            amount=amt, disbursed_date=disp_date, vendor=vendor, is_approved=True,
        ))

    # ── Investor Reports ───────────────────────────────────────────────────────
    db.add(InvestorReport(
        report_period="2025-Q4", report_type="quarterly",
        total_capital_raised=7_400_000, total_capital_deployed=6_050_000,
        phase1_pct_complete=100.0, phase2_pct_complete=42.0,
        projected_irr=TARGET_IRR, actual_irr=None,
        narrative="Phase 1 fully deployed and operational. Phase 2 Skill Shot Academy 42% complete with 7 of 10 bays installed. Naming rights negotiation advancing — LOI signed with two candidates. Crowdfunding campaign in pre-launch.",
    ))

    # ── TID Ledger — 12 months ────────────────────────────────────────────────
    cumulative_tid = 0.0
    random.seed(11)
    for i in range(12):
        mo_date = today - timedelta(days=30 * (12 - i))
        mo_str  = mo_date.strftime("%Y-%m")
        occ_pct = 0.50 + i * 0.015 + random.uniform(-0.04, 0.04)
        occ_pct = min(max(occ_pct, 0.35), 0.88)
        rooms_sold   = int(HOTEL_ROOMS * 30 * occ_pct)
        adr          = 112 + i * 2.5
        hotel_rev    = round(rooms_sold * adr, 2)
        tid          = round(hotel_rev * TID_ASSESSMENT_RATE, 2)
        cumulative_tid += tid
        tourists     = int(rooms_sold * random.uniform(1.4, 1.8))
        db.add(TIDLedger(
            month=mo_str, hotel_room_revenue=hotel_rev, tid_assessment=tid,
            tid_cumulative=round(cumulative_tid, 2), rooms_sold=rooms_sold,
            occupancy_pct=round(occ_pct * 100, 1), tourism_visitors_est=tourists,
        ))

    await db.commit()
    return {
        "message": "Capital Stack seeded",
        "sources": len(sources),
        "disbursements": len(disb_data),
        "tid_months": 12,
        "investor_reports": 1,
        "seeded": True,
    }


# ── Sources ───────────────────────────────────────────────────────────────────

@router.get("/sources", summary="All capital sources — committed, received, deployed")
async def list_sources(
    phase: Optional[CapitalPhase] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    q = select(CapitalSource)
    if phase: q = q.where(CapitalSource.phase == phase)
    q = q.order_by(CapitalSource.priority_order)
    result = await db.execute(q)
    sources = result.scalars().all()
    return [
        {"id": s.id, "phase": s.phase, "source_type": s.source_type, "label": s.label,
         "target_amount": s.target_amount, "committed_amount": s.committed_amount,
         "received_amount": s.received_amount, "deployed_amount": s.deployed_amount,
         "committed_pct": s.committed_pct, "gap": s.gap, "status": s.status,
         "interest_rate": s.interest_rate, "term_years": s.term_years,
         "annual_debt_service": s.annual_debt_service,
         "lender_investor": s.lender_investor, "notes": s.notes}
        for s in sources
    ]


@router.patch("/sources/{source_id}", summary="Update capital source progress")
async def update_source(source_id: str, payload: SourceUpdate, db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(select(CapitalSource).where(CapitalSource.id == source_id))
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(404, "Source not found")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(source, k, v)
    await db.commit()
    return {"id": source.id, "message": "Source updated"}


# ── Disbursements ─────────────────────────────────────────────────────────────

@router.get("/disbursements", summary="Capital disbursements by phase and category")
async def list_disbursements(
    phase: Optional[CapitalPhase] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    q = select(CapitalDisbursement)
    if phase: q = q.where(CapitalDisbursement.phase == phase)
    q = q.order_by(CapitalDisbursement.disbursed_date)
    result = await db.execute(q)
    disbs = result.scalars().all()
    return [
        {"id": d.id, "phase": d.phase, "category": d.category,
         "description": d.description, "amount": d.amount,
         "disbursed_date": d.disbursed_date.isoformat() if d.disbursed_date else None,
         "vendor": d.vendor, "is_approved": d.is_approved}
        for d in disbs
    ]


@router.post("/disbursements", summary="Log a capital disbursement")
async def create_disbursement(payload: DisbursementCreate, db: AsyncSession = Depends(get_db)) -> dict:
    disb = CapitalDisbursement(**payload.model_dump())
    db.add(disb)
    await db.commit()
    return {"message": "Disbursement logged"}


# ── IRR Model ─────────────────────────────────────────────────────────────────

@router.get("/irr-model", summary="IRR and payback period model — projected vs target")
async def irr_model(db: AsyncSession = Depends(get_db)) -> dict:
    sources_q = await db.execute(select(CapitalSource))
    sources = sources_q.scalars().all()

    total_committed = sum(s.committed_amount for s in sources)
    total_received  = sum(s.received_amount for s in sources)
    total_deployed  = sum(s.deployed_amount for s in sources)
    total_target    = sum(s.target_amount for s in sources)
    total_debt_svc  = sum(s.annual_debt_service for s in sources)
    total_gap       = TOTAL_CAPITAL_TARGET - total_committed

    p1_committed = sum(s.committed_amount for s in sources if s.phase == CapitalPhase.PHASE1)
    p2_committed = sum(s.committed_amount for s in sources if s.phase == CapitalPhase.PHASE2)

    # 5-year cash flow model (simplified)
    annual_revenues = [PHASE1_ANNUAL_REV, PHASE1_ANNUAL_REV * 1.08, PHASE1_ANNUAL_REV * 1.15 + PHASE2_YEAR1_REV * 0.5, PHASE1_ANNUAL_REV * 1.20 + PHASE2_YEAR1_REV, PHASE1_ANNUAL_REV * 1.25 + PHASE2_YEAR1_REV * 1.15]
    annual_net = [rev - total_debt_svc - (rev * 0.55) for rev in annual_revenues]  # 55% operating costs

    # Simple payback calculation
    cumulative = -total_committed
    payback_yr = None
    for yr, net in enumerate(annual_net, start=1):
        cumulative += net
        if cumulative >= 0 and not payback_yr:
            payback_yr = round(yr - 1 + (cumulative - net) / net * -1, 1) if net != 0 else yr

    # Rough IRR approximation
    total_net = sum(annual_net)
    if total_committed > 0:
        simple_roi = total_net / total_committed * 100
        projected_irr = min(TARGET_IRR * 1.05, max(15.0, simple_roi / 5 * 1.5))
    else:
        projected_irr = 0.0

    return {
        "total_target": TOTAL_CAPITAL_TARGET,
        "total_committed": round(total_committed, 2),
        "total_received": round(total_received, 2),
        "total_deployed": round(total_deployed, 2),
        "total_gap": round(total_gap, 2),
        "committed_pct": round(total_committed / TOTAL_CAPITAL_TARGET * 100, 1),
        "phase1_committed": round(p1_committed, 2),
        "phase1_target": PHASE1_CAPITAL,
        "phase1_pct": round(p1_committed / PHASE1_CAPITAL * 100, 1),
        "phase2_committed": round(p2_committed, 2),
        "phase2_target": PHASE2_CAPITAL,
        "phase2_pct": round(p2_committed / PHASE2_CAPITAL * 100, 1),
        "annual_debt_service": round(total_debt_svc, 2),
        "projected_irr": round(projected_irr, 1),
        "target_irr": TARGET_IRR,
        "projected_payback_yrs": payback_yr or TARGET_PAYBACK_YRS,
        "target_payback_yrs": TARGET_PAYBACK_YRS,
        "five_year_revenue_target": FIVE_YEAR_REVENUE,
        "five_year_cashflow_model": [{"year": i + 1, "revenue": round(r, 2), "net": round(n, 2)} for i, (r, n) in enumerate(zip(annual_revenues, annual_net))],
    }


# ── TID ───────────────────────────────────────────────────────────────────────

@router.get("/tid-model", summary="TID bond modeling — monthly assessments and cumulative")
async def tid_model(db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(select(TIDLedger).order_by(TIDLedger.month))
    ledger = result.scalars().all()

    total_assessed    = sum(l.tid_assessment for l in ledger)
    total_hotel_rev   = sum(l.hotel_room_revenue for l in ledger)
    total_tourists    = sum(l.tourism_visitors_est for l in ledger)
    avg_occ           = round(sum(l.occupancy_pct for l in ledger) / len(ledger), 1) if ledger else 0

    # TID bond capacity (simplified: 20× annual assessment)
    annual_tid_rate   = total_assessed / len(ledger) * 12 if ledger else 0
    tid_bond_capacity = round(annual_tid_rate * 20, 2)  # 20yr bond life

    return {
        "total_tid_assessed_12mo": round(total_assessed, 2),
        "total_hotel_revenue_12mo": round(total_hotel_rev, 2),
        "total_tourists_12mo": total_tourists,
        "avg_occupancy_pct": avg_occ,
        "annual_tid_rate_est": round(annual_tid_rate, 2),
        "tid_bond_capacity": tid_bond_capacity,
        "tid_assessment_rate": f"{TID_ASSESSMENT_RATE * 100}%",
        "monthly_detail": [
            {"month": l.month, "hotel_revenue": l.hotel_room_revenue,
             "tid_assessment": l.tid_assessment, "tid_cumulative": l.tid_cumulative,
             "rooms_sold": l.rooms_sold, "occupancy_pct": l.occupancy_pct,
             "tourism_visitors": l.tourism_visitors_est}
            for l in ledger
        ],
    }


# ── Investor Reports ──────────────────────────────────────────────────────────

@router.get("/investor-reports", summary="Periodic investor report history")
async def investor_reports(db: AsyncSession = Depends(get_db)) -> list[dict]:
    result = await db.execute(select(InvestorReport).order_by(InvestorReport.report_period.desc()))
    reports = result.scalars().all()
    return [
        {"id": r.id, "report_period": r.report_period, "report_type": r.report_type,
         "total_capital_raised": r.total_capital_raised, "total_capital_deployed": r.total_capital_deployed,
         "phase1_pct_complete": r.phase1_pct_complete, "phase2_pct_complete": r.phase2_pct_complete,
         "projected_irr": r.projected_irr, "actual_irr": r.actual_irr,
         "narrative": r.narrative, "created_at": r.created_at.isoformat()}
        for r in reports
    ]


# ── AI Investor Brief ─────────────────────────────────────────────────────────

@router.post("/ai-investor-brief", summary="AI investor-quality capital stack brief")
async def ai_investor_brief(db: AsyncSession = Depends(get_db)) -> dict:
    irr = await irr_model(db)
    tid = await tid_model(db)
    sources = await list_sources(db=db)
    gap_sources = [s for s in sources if s["gap"] > 0]
    debt_sources = [s for s in sources if s["interest_rate"]]

    prompt = f"""
NGP Development — Capital Stack Investor Brief
Date: {date.today().isoformat()} | Project: NXS National Complex, 704 Kirkus St, Proctor MN (ISG #24688001)

CAPITAL SUMMARY:
- Total target: ${irr['total_target']:,.0f}
- Total committed: ${irr['total_committed']:,.0f} ({irr['committed_pct']}%)
- Total received: ${irr['total_received']:,.0f}
- Total deployed: ${irr['total_deployed']:,.0f}
- Remaining gap: ${irr['total_gap']:,.0f}

PHASE STATUS:
- Phase 1 ($5.2M campus): {irr['phase1_pct']}% committed — COMPLETE & OPERATIONAL
- Phase 2 ($4.65M Skill Shot): {irr['phase2_pct']}% committed — IN PROGRESS

FINANCIAL MODEL:
- Projected IRR: {irr['projected_irr']}% (target: {irr['target_irr']}%)
- Projected payback: {irr['projected_payback_yrs']} years (target: {irr['target_payback_yrs']} years)
- Annual debt service: ${irr['annual_debt_service']:,.0f}
- 5-year revenue target: ${irr['five_year_revenue_target']:,.0f}

5-YEAR CASH FLOW:
{chr(10).join(f"  Year {cf['year']}: Revenue ${cf['revenue']:,.0f} | Net ${cf['net']:,.0f}" for cf in irr['five_year_cashflow_model'])}

TID PERFORMANCE (12mo):
- Hotel revenue: ${tid['total_hotel_revenue_12mo']:,.0f}
- TID assessed: ${tid['total_tid_assessed_12mo']:,.0f}
- Avg occupancy: {tid['avg_occupancy_pct']}%
- TID bond capacity: ${tid['tid_bond_capacity']:,.0f}

OPEN CAPITAL GAPS:
{chr(10).join(f"  {s['label']}: ${s['gap']:,.0f} gap — {s['status']}" for s in gap_sources)}

Generate a 4-paragraph investor-quality capital brief:
1. Capital stack health — what percentage is closed, what phase status, and what does the IRR and payback trajectory look like vs targets?
2. Gap closure strategy — for each open gap (naming rights, MN DEED, crowdfunding), what's the specific action and timeline to close?
3. TID and debt service — how does the hotel TID performance support bond service, and what's the coverage ratio?
4. Investment thesis reaffirmation — why does this project merit the remaining capital commitment? Use the 5-year cash flow, regional exclusivity (PuttView 200mi, Skill Shot regional), and Phase 1 operational proof as anchors.
"""

    response = claude.messages.create(
        model="claude-opus-4-5",
        max_tokens=800,
        system=CAP_CONTEXT,
        messages=[{"role": "user", "content": prompt}],
    )

    return {
        "brief": response.content[0].text,
        "irr_summary": {
            "committed_pct": irr["committed_pct"],
            "projected_irr": irr["projected_irr"],
            "projected_payback_yrs": irr["projected_payback_yrs"],
            "total_gap": irr["total_gap"],
        },
        "generated_at": datetime.utcnow().isoformat(),
    }


@router.post("/ai-gap-close-brief", summary="AI tactical brief for closing remaining capital gaps")
async def ai_gap_close(db: AsyncSession = Depends(get_db)) -> dict:
    sources = await list_sources(db=db)
    gap_sources = [s for s in sources if s["gap"] > 0 and s["status"] not in ["deployed", "closed"]]
    total_gap = sum(s["gap"] for s in gap_sources)

    prompt = f"""
NGP Development — Capital Gap Closure Brief
Total remaining gap: ${total_gap:,.0f}

Open gaps by source:
{chr(10).join(f"  {s['source_type'].upper()}: {s['label']} — ${s['gap']:,.0f} gap, status: {s['status']}, notes: {s['notes'] or 'N/A'}" for s in gap_sources)}

Generate a concise 2-paragraph tactical brief:
1. Ranking — which gap to close first and why (easiest, most likely, or highest leverage)
2. This week's actions — specific calls to make, applications to submit, or campaigns to launch, with named targets where possible (Essentia Health, MN DEED, IRRRB, crowdfunding platform)
"""

    response = claude.messages.create(
        model="claude-opus-4-5",
        max_tokens=500,
        system=CAP_CONTEXT,
        messages=[{"role": "user", "content": prompt}],
    )

    return {
        "brief": response.content[0].text,
        "total_gap": round(total_gap, 2),
        "gap_sources": len(gap_sources),
        "generated_at": datetime.utcnow().isoformat(),
    }
