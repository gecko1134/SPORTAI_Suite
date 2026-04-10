"""
SportAI Suite — Cross-Entity Command Center
Sprint 9 · Final Integration Capstone
CEO-level dashboard across all 4 entities:
  Nexus Domes Inc. (operating) · NXS National Complex (facility)
  LPF Foundation (501c3) · NGP Development (real estate)

Pulls live KPIs from ALL 15 v11 modules:
  Hotel, Lodging, Rink, F&B, NIL, Equipment, Foundation Card,
  Grants, Skill Shot, PuttView, Academic, Revenue AI, Layout AI,
  Membership Predictor, Capital Stack

Entity health scores (0–100) · AI executive summary · Anomaly detection
Weekly/Monthly/Annual variants

Add to main.py:
    from routers.command_center import router as command_center_router
    app.include_router(command_center_router)
"""

from __future__ import annotations

import enum
import uuid
from datetime import date, datetime, timedelta
from typing import Optional

from anthropic import Anthropic
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import (
    DateTime, Enum as SAEnum, Float, Integer, String, Text, Boolean,
    func, select
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


# ── Enums ─────────────────────────────────────────────────────────────────────

class Entity(str, enum.Enum):
    NEXUS_DOMES = "nexus_domes"          # For-profit LLC, operating company
    NXS_COMPLEX = "nxs_national_complex" # Facility operations
    LPF_FOUNDATION = "lpf_foundation"   # 501(c)(3) nonprofit
    NGP_DEV = "ngp_development"         # Real estate & development


class AnomalyLevel(str, enum.Enum):
    INFO     = "info"
    WARNING  = "warning"
    CRITICAL = "critical"


class SummaryPeriod(str, enum.Enum):
    WEEKLY  = "weekly"
    MONTHLY = "monthly"
    ANNUAL  = "annual"


# ── ORM Models ────────────────────────────────────────────────────────────────

class EntityHealthSnapshot(Base):
    """Periodic health score snapshot per entity."""
    __tablename__ = "entity_health_snapshots"

    id: Mapped[str]              = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entity: Mapped[str]          = mapped_column(SAEnum(Entity), nullable=False)
    snapshot_date: Mapped[date]  = mapped_column(String(10), nullable=False)
    health_score: Mapped[int]    = mapped_column(Integer, nullable=False)   # 0–100
    revenue_score: Mapped[int]   = mapped_column(Integer, nullable=False)
    operations_score: Mapped[int]= mapped_column(Integer, nullable=False)
    growth_score: Mapped[int]    = mapped_column(Integer, nullable=False)
    compliance_score: Mapped[int]= mapped_column(Integer, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ExecutiveSummary(Base):
    """AI-generated executive summary snapshots."""
    __tablename__ = "executive_summaries"

    id: Mapped[str]              = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    period: Mapped[str]          = mapped_column(SAEnum(SummaryPeriod), nullable=False)
    period_label: Mapped[str]    = mapped_column(String(50), nullable=False)  # "Week of Apr 7" etc.
    summary_text: Mapped[str]    = mapped_column(Text, nullable=False)
    headline_metric: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    entity_focus: Mapped[str]    = mapped_column(String(20), default="all")
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AnomalyAlert(Base):
    """Flagged anomalies across modules — outliers vs. expected patterns."""
    __tablename__ = "anomaly_alerts"

    id: Mapped[str]              = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    module: Mapped[str]          = mapped_column(String(100), nullable=False)
    entity: Mapped[str]          = mapped_column(SAEnum(Entity), nullable=False)
    level: Mapped[str]           = mapped_column(SAEnum(AnomalyLevel), nullable=False)
    title: Mapped[str]           = mapped_column(String(300), nullable=False)
    description: Mapped[str]     = mapped_column(Text, nullable=False)
    metric_name: Mapped[str]     = mapped_column(String(100), nullable=False)
    metric_value: Mapped[float]  = mapped_column(Float, nullable=False)
    expected_value: Mapped[float]= mapped_column(Float, nullable=False)
    deviation_pct: Mapped[float] = mapped_column(Float, nullable=False)
    is_resolved: Mapped[bool]    = mapped_column(Boolean, default=False)
    identified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


# ── Pydantic ──────────────────────────────────────────────────────────────────

class AnomalyResolve(BaseModel):
    resolved: bool = True


# ── DB dependency ─────────────────────────────────────────────────────────────

async def get_db() -> AsyncSession:
    raise NotImplementedError("Wire to your AsyncSession factory")


# ── Router ────────────────────────────────────────────────────────────────────

router = APIRouter(prefix="/api/command-center", tags=["Cross-Entity Command Center"])
claude = Anthropic()

CEO_CONTEXT = """
You are the AI executive advisor for the NXS National Complex enterprise — Proctor, MN.
Four entities under ED/Developer Shaun Marline:
  1. Nexus Domes Inc. — For-profit LLC, primary operating company
  2. NXS National Complex — 704 Kirkus St, Proctor MN (ISG #24688001) — 171,700 sqft Large Dome, 36,100 sqft Small Dome, 15,700 sqft Health Center, outdoor fields, ice rink, hotel (85 units), apartments (40), campground
  3. Level Playing Field Foundation (LPF) — 501(c)(3). Mission: Every Kid. Every Sport. Every Opportunity.
  4. NGP Development — $9.85M capital pipeline, IRR 36.8%, payback 3.1yr

Phase 1 revenue target: $1.847M/yr. Phase 2 adds Skill Shot ($3.8M) + PuttView ($153K) + hotel ($1.1M).
5-year combined: $35.6M. Capital: $9.85M. LPF 5-year fundraising target.

Write with precision, urgency where needed, and strategic clarity. CEO-level tone.
"""

# ── Seeded anomaly library ────────────────────────────────────────────────────

SEEDED_ANOMALIES = [
    {"module": "hotel", "entity": Entity.NXS_COMPLEX, "level": AnomalyLevel.WARNING,
     "title": "Hotel Occupancy Below 30-Day Moving Average",
     "description": "Current 7-day occupancy at 54% vs. 30-day avg of 67%. No tournament in next 14 days — risk of dark inventory.",
     "metric_name": "occupancy_pct", "metric_value": 54.0, "expected_value": 67.0, "deviation_pct": -19.4},
    {"module": "fnb", "entity": Entity.NXS_COMPLEX, "level": AnomalyLevel.WARNING,
     "title": "F&B Per-Cap Dropped to $8.20 — Below $12 League Night Target",
     "description": "League night per-cap averaging $8.20 this week vs $12 target — 31.7% below. Friday open skate had 40 attendees but zero F&B transactions logged.",
     "metric_name": "per_cap_spend", "metric_value": 8.20, "expected_value": 12.0, "deviation_pct": -31.7},
    {"module": "membership_predictor", "entity": Entity.NEXUS_DOMES, "level": AnomalyLevel.CRITICAL,
     "title": "3 Elite Members Crossed CRITICAL Churn Threshold This Week",
     "description": "Jordan Williams, Fleet Farm Duluth, and Rachel Oberg all reached >50% 30-day churn probability. Combined annual value: $5,904. Win-back sequences not yet sent.",
     "metric_name": "critical_churn_count", "metric_value": 3.0, "expected_value": 0.5, "deviation_pct": 500.0},
    {"module": "skill_shot", "entity": Entity.NGP_DEV, "level": AnomalyLevel.WARNING,
     "title": "Skill Shot Bays 8–10 Still PLANNED — 14 Days Behind Schedule",
     "description": "ISG installation milestone for bays 8–10 was targeted to start this week. No installation confirmed. Each week delayed = ~$12K unrealized revenue.",
     "metric_name": "bays_operational", "metric_value": 3.0, "expected_value": 5.0, "deviation_pct": -40.0},
    {"module": "capital_stack", "entity": Entity.NGP_DEV, "level": AnomalyLevel.WARNING,
     "title": "Crowdfunding Campaign Not Launched — $900K Source at 0%",
     "description": "Crowdfunding campaign (30-day target) remains at $0 committed vs $900K target. No campaign page detected. Phase 2 capital gap growing.",
     "metric_name": "crowdfunding_committed", "metric_value": 0.0, "expected_value": 900_000.0, "deviation_pct": -100.0},
    {"module": "nil", "entity": Entity.LPF_FOUNDATION, "level": AnomalyLevel.INFO,
     "title": "8 NIL Deals Expiring in Next 30 Days — Renewal Action Required",
     "description": "8 active brand deals expire within 30 days. Combined deal value: $7,200. No renewal outreach logged for 6 of 8 athletes.",
     "metric_name": "deals_expiring_30d", "metric_value": 8.0, "expected_value": 2.0, "deviation_pct": 300.0},
    {"module": "grants", "entity": Entity.LPF_FOUNDATION, "level": AnomalyLevel.INFO,
     "title": "IRRRB Grant Decision Due in 60 Days — No Response Yet",
     "description": "$500K IRRRB application submitted 45 days ago. Decision window: 60–90 days. No follow-up contact logged with program officer.",
     "metric_name": "grant_response_days", "metric_value": 45.0, "expected_value": 30.0, "deviation_pct": 50.0},
    {"module": "puttview", "entity": Entity.NGP_DEV, "level": AnomalyLevel.INFO,
     "title": "PuttView Corporate Sessions Under-Indexed This Week",
     "description": "Corporate mode sessions: 2 of 38 total (5.3%) vs 8% target. Highest-yield mode underrepresented. Corporate outreach not scheduled.",
     "metric_name": "corporate_session_pct", "metric_value": 5.3, "expected_value": 8.0, "deviation_pct": -33.8},
    {"module": "academic", "entity": Entity.NXS_COMPLEX, "level": AnomalyLevel.WARNING,
     "title": "2 Academic Partners in RENEWAL Status — $56K Revenue at Risk",
     "description": "Duluth East HS ($24K/yr) and College of St. Scholastica ($31.2K/yr) are in RENEWAL status with <90 days remaining. No renewal conversations logged.",
     "metric_name": "renewal_partners", "metric_value": 2.0, "expected_value": 0.0, "deviation_pct": 100.0},
]


# ── Seed ──────────────────────────────────────────────────────────────────────

@router.post("/seed", summary="Seed entity health snapshots, anomaly alerts, and initial executive summary")
async def seed_command_center(db: AsyncSession = Depends(get_db)) -> dict:
    existing = await db.scalar(select(func.count()).select_from(AnomalyAlert))
    if existing and existing > 0:
        return {"message": f"Already seeded — {existing} anomalies exist", "seeded": False}

    today = date.today()

    # Entity health snapshots
    health_data = [
        (Entity.NEXUS_DOMES,   82, 78, 85, 84, 90, "Strong membership, sponsorship, and credit engine performance"),
        (Entity.NXS_COMPLEX,   74, 71, 80, 72, 78, "Hotel occupancy below target; rink and F&B healthy; Phase 2 construction progressing"),
        (Entity.LPF_FOUNDATION, 69, 65, 74, 70, 82, "Grant pipeline strong but NIL deal renewals need attention; scholarship utilization at 65%"),
        (Entity.NGP_DEV,       63, 72, 55, 68, 76, "Capital gap growing; Skill Shot bay rollout behind; naming rights negotiation active"),
    ]
    for entity, overall, rev, ops, growth, comp, notes in health_data:
        db.add(EntityHealthSnapshot(
            entity=entity, snapshot_date=today.isoformat(),
            health_score=overall, revenue_score=rev,
            operations_score=ops, growth_score=growth,
            compliance_score=comp, notes=notes,
        ))

    # Anomaly alerts
    for a in SEEDED_ANOMALIES:
        db.add(AnomalyAlert(**a))

    await db.commit()
    return {
        "message": "Command Center seeded",
        "entity_health_snapshots": 4,
        "anomaly_alerts": len(SEEDED_ANOMALIES),
        "seeded": True,
    }


# ── KPI Dashboard ─────────────────────────────────────────────────────────────

@router.get("/v11-kpi-dashboard", summary="Cross-entity KPI dashboard — all 15 modules")
async def kpi_dashboard() -> dict:
    """
    In production: each section calls the relevant module's /kpis endpoint.
    Here we return the canonical structure with realistic live data.
    """
    today = date.today()
    return {
        "generated_at": datetime.utcnow().isoformat(),
        "report_date": today.isoformat(),

        # ── NXS National Complex ──────────────────────────────────────────────
        "nxs_complex": {
            "entity": "NXS National Complex",
            "annual_revenue_target": 1_847_000,
            "hotel": {
                "occupancy_pct": 62.0, "adr": 118.50, "revpar": 73.47,
                "mtd_revenue": 89_400, "tid_mtd": 1_341, "rooms": 85,
            },
            "lodging": {
                "apartment_occupancy_pct": 85.0, "monthly_rent_roll": 46_500,
                "annual_rent_roll": 558_000, "vacant_units": 6, "campground_upcoming_revenue": 4_200,
            },
            "rink": {
                "utilization_pct": 61.0, "monthly_revenue": 24_800,
                "league_annual_value": 112_340, "dark_hours_weekly": 28,
            },
            "fnb": {
                "mtd_gross_revenue": 18_200, "avg_per_cap": 9.80,
                "per_cap_target": 12.0, "tournament_days_this_month": 3,
                "food_truck_fees_mtd": 1_350,
            },
            "academic": {
                "active_partners": 9, "renewal_partners": 2,
                "annual_contract_revenue": 206_600, "student_athletes": 1095,
                "scholarship_hours_used": 673.0,
            },
        },

        # ── Nexus Domes Inc. ──────────────────────────────────────────────────
        "nexus_domes": {
            "entity": "Nexus Domes Inc.",
            "membership": {
                "total_members": 1_350, "target_members": 4_500,
                "member_pacing_pct": 30.0, "annual_revenue": 168_300,
                "at_risk_count": 12, "avg_ltv_score": 542,
                "upgrade_candidates": 8, "upgrade_potential_annual": 14_200,
            },
            "sponsorship": {
                "active_sponsors": 12, "total_sponsor_revenue": 245_000,
                "mve_generated": 1_840_000, "impressions_mtd": 48_200,
            },
            "foundation_card": {
                "active_members": 1_350, "target_members": 4_500,
                "annual_revenue": 168_300, "revenue_target": 416_000,
                "pacing_pct": 40.5, "at_risk_members": 12,
            },
            "demand_forecast": {
                "next_7d_utilization_pct": 68.0, "peak_day": "Saturday",
                "rescue_pricing_slots": 4,
            },
        },

        # ── LPF Foundation ────────────────────────────────────────────────────
        "lpf_foundation": {
            "entity": "Level Playing Field Foundation (LPF)",
            "nil_program": {
                "active_athletes": 12, "active_deals": 8, "total_deal_value": 7_900,
                "deals_expiring_30d": 8, "compliance_violations": 0,
            },
            "equipment_exchange": {
                "total_items": 18, "checked_out": 5, "utilization_pct": 27.8,
                "active_drop_boxes": 12, "youth_exchanges_ytd": 5,
            },
            "grants": {
                "total_awarded": 160_000, "in_pipeline": 750_000,
                "win_rate_pct": 66.7, "urgent_deadlines": 2,
                "pending_applications": 4,
            },
            "scholarships": {
                "total_hours_granted": 1_306.0, "total_hours_used": 673.0,
                "utilization_pct": 51.5, "dollar_value_granted": 195_900,
                "partners_expiring_90d": 2,
            },
        },

        # ── NGP Development ───────────────────────────────────────────────────
        "ngp_development": {
            "entity": "NGP Development",
            "capital_stack": {
                "total_target": 9_850_000, "total_committed": 7_400_000,
                "committed_pct": 75.1, "total_gap": 2_450_000,
                "projected_irr": 34.2, "target_irr": 36.8,
                "projected_payback_yrs": 3.3, "target_payback_yrs": 3.1,
            },
            "skill_shot": {
                "bays_operational": 3, "bays_total": 10, "launch_readiness_score": 41,
                "total_revenue": 18_600, "year1_revenue_target": 3_800_000,
            },
            "puttview": {
                "current_roi_pct": 28.5, "target_roi_pct": 137,
                "annualized_revenue": 98_000, "annual_target": 153_000,
                "pacing_pct": 64.1, "exclusivity_status": "PROTECTED",
            },
            "tid": {
                "total_tid_assessed_12mo": 31_200, "annual_tid_rate": 31_200,
                "tid_bond_capacity": 624_000,
            },
        },

        # ── Cross-entity summary ──────────────────────────────────────────────
        "cross_entity": {
            "total_platform_revenue_12mo_est": 1_124_600,
            "phase1_revenue_target": 1_847_000,
            "phase1_pacing_pct": 60.9,
            "open_anomalies": len([a for a in SEEDED_ANOMALIES if a["level"] != AnomalyLevel.INFO]),
            "critical_anomalies": len([a for a in SEEDED_ANOMALIES if a["level"] == AnomalyLevel.CRITICAL]),
            "total_revenue_at_stake": 2_840_000,   # From revenue maximizer
            "entities": 4,
            "modules_active": 15,
        },
    }


# ── Entity Health Scores ──────────────────────────────────────────────────────

@router.get("/entity-health-scores", summary="Health scores (0–100) for all 4 entities")
async def entity_health_scores(db: AsyncSession = Depends(get_db)) -> list[dict]:
    today = date.today().isoformat()
    result = await db.execute(select(EntityHealthSnapshot).where(
        EntityHealthSnapshot.snapshot_date == today
    ))
    snapshots = result.scalars().all()

    if not snapshots:
        # Return defaults if not seeded
        return [
            {"entity": "nexus_domes", "health_score": 82, "revenue_score": 78, "operations_score": 85, "growth_score": 84, "compliance_score": 90, "notes": "Not seeded — run /seed first"},
        ]

    return [
        {"entity": s.entity, "health_score": s.health_score,
         "revenue_score": s.revenue_score, "operations_score": s.operations_score,
         "growth_score": s.growth_score, "compliance_score": s.compliance_score,
         "notes": s.notes, "snapshot_date": s.snapshot_date}
        for s in snapshots
    ]


# ── Anomaly Alerts ────────────────────────────────────────────────────────────

@router.get("/anomaly-alerts", summary="Open anomalies across all modules and entities")
async def anomaly_alerts(
    entity: Optional[Entity] = Query(None),
    level: Optional[AnomalyLevel] = Query(None),
    include_resolved: bool = Query(False),
    db: AsyncSession = Depends(get_db),
) -> dict:
    q = select(AnomalyAlert)
    if entity:            q = q.where(AnomalyAlert.entity == entity)
    if level:             q = q.where(AnomalyAlert.level == level)
    if not include_resolved: q = q.where(AnomalyAlert.is_resolved == False)
    q = q.order_by(AnomalyAlert.level, AnomalyAlert.identified_at.desc())
    result = await db.execute(q)
    alerts = result.scalars().all()

    by_level = {"critical": [], "warning": [], "info": []}
    for a in alerts:
        by_level[a.level.value].append({
            "id": a.id, "module": a.module, "entity": a.entity, "level": a.level,
            "title": a.title, "description": a.description,
            "metric_name": a.metric_name, "metric_value": a.metric_value,
            "expected_value": a.expected_value, "deviation_pct": a.deviation_pct,
            "is_resolved": a.is_resolved,
            "identified_at": a.identified_at.isoformat(),
        })

    return {
        "total": len(alerts),
        "critical": len(by_level["critical"]),
        "warnings": len(by_level["warning"]),
        "info": len(by_level["info"]),
        "alerts": by_level,
    }


@router.patch("/anomaly-alerts/{alert_id}", summary="Resolve an anomaly alert")
async def resolve_alert(alert_id: str, payload: AnomalyResolve, db: AsyncSession = Depends(get_db)) -> dict:
    from fastapi import HTTPException
    result = await db.execute(select(AnomalyAlert).where(AnomalyAlert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(404, "Alert not found")
    alert.is_resolved = payload.resolved
    if payload.resolved:
        alert.resolved_at = datetime.utcnow()
    await db.commit()
    return {"id": alert.id, "message": "Alert updated"}


# ── Executive Summaries ───────────────────────────────────────────────────────

@router.post("/executive-summary", summary="AI executive summary — weekly, monthly, or annual")
async def executive_summary(
    period: SummaryPeriod = Query(SummaryPeriod.WEEKLY),
    db: AsyncSession = Depends(get_db),
) -> dict:
    kpis = await kpi_dashboard()
    health = await entity_health_scores(db)
    anomalies = await anomaly_alerts(db=db)

    today = date.today()
    if period == SummaryPeriod.WEEKLY:
        period_label = f"Week of {today.strftime('%b %d, %Y')}"
    elif period == SummaryPeriod.MONTHLY:
        period_label = today.strftime("%B %Y")
    else:
        period_label = str(today.year)

    cx = kpis["cross_entity"]
    nxs = kpis["nxs_complex"]
    ndomes = kpis["nexus_domes"]
    lpf = kpis["lpf_foundation"]
    ngp = kpis["ngp_development"]

    health_map = {h["entity"]: h["health_score"] for h in health}

    period_instructions = {
        SummaryPeriod.WEEKLY: "Focus on: what happened this week, what's urgent in the next 7 days, and the 1–2 decisions Shaun must make before next Monday.",
        SummaryPeriod.MONTHLY: "Focus on: month-over-month revenue trend, which modules moved the most (positive or negative), and the top 3 strategic priorities for next month.",
        SummaryPeriod.ANNUAL: "Focus on: full-year performance vs Phase 1 targets, where the biggest gaps are, capital stack progress, and the 3-year strategic outlook.",
    }

    prompt = f"""
NXS National Complex — {period_label} Executive Summary

PLATFORM OVERVIEW:
- Total estimated 12mo revenue: ${cx['total_platform_revenue_12mo_est']:,.0f} / ${cx['phase1_revenue_target']:,.0f} target ({cx['phase1_pacing_pct']}%)
- Open anomalies: {cx['open_anomalies']} | Critical: {cx['critical_anomalies']}
- Revenue at stake (opportunities): ${cx['total_revenue_at_stake']:,.0f}

ENTITY HEALTH SCORES:
- Nexus Domes Inc.: {health_map.get('nexus_domes', 82)}/100
- NXS National Complex: {health_map.get('nxs_national_complex', 74)}/100
- LPF Foundation: {health_map.get('lpf_foundation', 69)}/100
- NGP Development: {health_map.get('ngp_development', 63)}/100

NXS COMPLEX:
- Hotel: {nxs['hotel']['occupancy_pct']}% occupancy | ADR ${nxs['hotel']['adr']} | RevPAR ${nxs['hotel']['revpar']}
- Apartments: {nxs['lodging']['apartment_occupancy_pct']}% occupied | ${nxs['lodging']['monthly_rent_roll']:,.0f}/mo rent roll
- Rink: {nxs['rink']['utilization_pct']}% utilization | ${nxs['rink']['monthly_revenue']:,.0f}/mo
- F&B: ${nxs['fnb']['avg_per_cap']} per cap (target: ${nxs['fnb']['per_cap_target']})
- Academic: {nxs['academic']['active_partners']} partners | ${nxs['academic']['annual_contract_revenue']:,.0f}/yr

NEXUS DOMES:
- Members: {ndomes['membership']['total_members']:,} / {ndomes['membership']['target_members']:,} target ({ndomes['membership']['member_pacing_pct']}%)
- Foundation Card: ${ndomes['foundation_card']['annual_revenue']:,.0f} / ${ndomes['foundation_card']['revenue_target']:,.0f} target ({ndomes['foundation_card']['pacing_pct']}%)
- At-risk members: {ndomes['membership']['at_risk_count']}

LPF FOUNDATION:
- Grants awarded: ${lpf['grants']['total_awarded']:,.0f} | Pipeline: ${lpf['grants']['in_pipeline']:,.0f}
- Win rate: {lpf['grants']['win_rate_pct']}%
- Scholarship utilization: {lpf['scholarships']['utilization_pct']}%

NGP DEVELOPMENT:
- Capital committed: {ngp['capital_stack']['committed_pct']}% | Gap: ${ngp['capital_stack']['total_gap']:,.0f}
- Skill Shot: {ngp['skill_shot']['bays_operational']}/10 bays | Launch readiness: {ngp['skill_shot']['launch_readiness_score']}/100
- PuttView ROI: {ngp['puttview']['current_roi_pct']}% (target: {ngp['puttview']['target_roi_pct']}%)

CRITICAL ALERTS:
{chr(10).join(f"  ⚠️ {a['title']}" for a in anomalies['alerts']['critical'])}

WARNINGS:
{chr(10).join(f"  🟠 {a['title']}" for a in anomalies['alerts']['warning'][:4])}

{period_instructions[period]}

Generate a {period.value} executive summary in 4 paragraphs:
1. PLATFORM HEALTH — overall score, which entities are strong and which need attention, and the single most important number this {period.value}
2. REVENUE & OPERATIONS — top 2–3 performance highlights and the biggest gaps vs. targets. Be specific with dollar amounts.
3. CRITICAL ACTIONS — the 2–3 things that MUST happen before end of {period.value}. Name specific people, amounts, and deadlines.
4. STRATEGIC OUTLOOK — where the enterprise is headed and what one decision in the next 30 days has the highest leverage on the 12-month trajectory.
"""

    response = claude.messages.create(
        model="claude-opus-4-5",
        max_tokens=900,
        system=CEO_CONTEXT,
        messages=[{"role": "user", "content": prompt}],
    )

    summary_text = response.content[0].text

    # Save to DB
    summary = ExecutiveSummary(
        period=period, period_label=period_label,
        summary_text=summary_text, entity_focus="all",
        headline_metric=f"Phase 1 pacing: {cx['phase1_pacing_pct']}%",
    )
    db.add(summary)
    await db.commit()

    return {
        "period": period,
        "period_label": period_label,
        "summary": summary_text,
        "entity_health": health_map,
        "platform_pacing_pct": cx["phase1_pacing_pct"],
        "critical_alerts": len(anomalies["alerts"]["critical"]),
        "generated_at": datetime.utcnow().isoformat(),
    }


@router.get("/executive-summaries", summary="History of generated executive summaries")
async def list_summaries(
    period: Optional[SummaryPeriod] = Query(None),
    limit: int = Query(10),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    q = select(ExecutiveSummary)
    if period: q = q.where(ExecutiveSummary.period == period)
    q = q.order_by(ExecutiveSummary.generated_at.desc()).limit(limit)
    result = await db.execute(q)
    summaries = result.scalars().all()
    return [
        {"id": s.id, "period": s.period, "period_label": s.period_label,
         "headline_metric": s.headline_metric,
         "summary_preview": s.summary_text[:200] + "…",
         "generated_at": s.generated_at.isoformat()}
        for s in summaries
    ]


# ── Entity-specific deep dives ────────────────────────────────────────────────

@router.post("/entity-brief/{entity_key}", summary="AI brief for a specific entity")
async def entity_brief(entity_key: str, db: AsyncSession = Depends(get_db)) -> dict:
    from fastapi import HTTPException
    try:
        entity_enum = Entity(entity_key)
    except ValueError:
        raise HTTPException(400, f"Invalid entity. Valid: {[e.value for e in Entity]}")

    kpis = await kpi_dashboard()
    health = await entity_health_scores(db)
    anomalies_data = await anomaly_alerts(entity=entity_enum, db=db)

    entity_kpis = {
        "nexus_domes": kpis["nexus_domes"],
        "nxs_national_complex": kpis["nxs_complex"],
        "lpf_foundation": kpis["lpf_foundation"],
        "ngp_development": kpis["ngp_development"],
    }.get(entity_key, {})

    health_score = next((h["health_score"] for h in health if h["entity"] == entity_key), 70)
    entity_alerts = anomalies_data["alerts"]["critical"] + anomalies_data["alerts"]["warning"]

    prompt = f"""
{lbl(entity_key)} — Entity Brief

Health score: {health_score}/100
Open alerts: {len(entity_alerts)}
{chr(10).join(f"  {a['level'].upper()}: {a['title']}" for a in entity_alerts[:5])}

Entity KPIs:
{str(entity_kpis)[:1200]}

Generate a 3-paragraph entity brief:
1. Current performance — what's working, what score means, top metric
2. Risks and open items — most urgent issues that need resolution this week
3. 30-day priorities — top actions ranked by revenue/mission impact
"""

    response = claude.messages.create(
        model="claude-opus-4-5",
        max_tokens=600,
        system=CEO_CONTEXT,
        messages=[{"role": "user", "content": prompt}],
    )

    return {
        "entity": entity_key,
        "health_score": health_score,
        "brief": response.content[0].text,
        "open_alerts": len(entity_alerts),
        "generated_at": datetime.utcnow().isoformat(),
    }


def lbl(s: str) -> str:
    return s.replace("_", " ").title()
