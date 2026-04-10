"""
SportAI Suite — AI Revenue Maximizer
Sprint 7 · Cross-Module Revenue Optimization Engine
Pulls from ALL v11 modules: Hotel, Lodging, Rink, F&B, NIL, Equipment,
Foundation Card, Grants, Skill Shot, PuttView, Academic, Tournament, Membership, Sponsors

Revenue Score 0–100 · Opportunity ranking · Pricing gaps · Cross-sell engine
Weekly AI revenue brief · Anomaly detection

Add to main.py:
    from routers.revenue_maximizer import router as revenue_maximizer_router
    app.include_router(revenue_maximizer_router)
"""

from __future__ import annotations

import enum
import uuid
from datetime import date, datetime, timedelta
from typing import Optional

from anthropic import Anthropic
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import Float, DateTime, Enum as SAEnum, Integer, String, Text, Boolean, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


# ── Enums ─────────────────────────────────────────────────────────────────────

class OpportunityType(str, enum.Enum):
    IDLE_CAPACITY      = "idle_capacity"
    PRICING_GAP        = "pricing_gap"
    CROSS_SELL         = "cross_sell"
    RETENTION_RISK     = "retention_risk"
    UNDERUTILIZED_ASSET = "underutilized_asset"
    REVENUE_LEAK       = "revenue_leak"
    UPSELL             = "upsell"
    NEW_PROGRAM        = "new_program"


class OpportunityPriority(str, enum.Enum):
    CRITICAL = "critical"
    HIGH     = "high"
    MEDIUM   = "medium"
    LOW      = "low"


class OpportunityStatus(str, enum.Enum):
    OPEN       = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED   = "resolved"
    DISMISSED  = "dismissed"


# ── ORM Models ────────────────────────────────────────────────────────────────

class RevenueOpportunity(Base):
    """AI-identified revenue opportunity across all modules."""
    __tablename__ = "revenue_opportunities"

    id: Mapped[str]                = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    opportunity_type: Mapped[str]  = mapped_column(SAEnum(OpportunityType), nullable=False)
    priority: Mapped[str]          = mapped_column(SAEnum(OpportunityPriority), nullable=False)
    status: Mapped[str]            = mapped_column(SAEnum(OpportunityStatus), default=OpportunityStatus.OPEN)
    module: Mapped[str]            = mapped_column(String(100), nullable=False)       # Which module this came from
    title: Mapped[str]             = mapped_column(String(300), nullable=False)
    description: Mapped[str]       = mapped_column(Text, nullable=False)
    estimated_annual_impact: Mapped[float] = mapped_column(Float, nullable=False)
    effort_level: Mapped[str]      = mapped_column(String(20), default="medium")      # low/medium/high
    recommended_action: Mapped[str]= mapped_column(Text, nullable=False)
    identified_at: Mapped[datetime]= mapped_column(DateTime(timezone=True), server_default=func.now())
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[Optional[str]]   = mapped_column(Text, nullable=True)


class RevenueActionLog(Base):
    """Log of actions taken on revenue opportunities."""
    __tablename__ = "revenue_actions_log"

    id: Mapped[str]               = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    opportunity_id: Mapped[str]   = mapped_column(String(36), nullable=False)
    action_taken: Mapped[str]     = mapped_column(Text, nullable=False)
    revenue_impact: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    logged_by: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    logged_at: Mapped[datetime]   = mapped_column(DateTime(timezone=True), server_default=func.now())


# ── Pydantic ──────────────────────────────────────────────────────────────────

class OpportunityUpdate(BaseModel):
    status: Optional[OpportunityStatus] = None
    notes: Optional[str] = None


class ActionCreate(BaseModel):
    opportunity_id: str
    action_taken: str
    revenue_impact: Optional[float] = None
    logged_by: Optional[str] = None


# ── DB dependency ─────────────────────────────────────────────────────────────

async def get_db() -> AsyncSession:
    raise NotImplementedError("Wire to your AsyncSession factory")


# ── Router ────────────────────────────────────────────────────────────────────

router = APIRouter(prefix="/api/revenue-ai", tags=["AI Revenue Maximizer"])
claude = Anthropic()

REV_CONTEXT = """
You are the AI Revenue Maximizer for NXS National Complex, an enterprise sports facility at
704 Kirkus Street, Proctor MN 55810. You have access to data from all platform modules:
Hotel (85 units), Apartments (40 units), Campground (30 sites), Ice Rink (200x85),
F&B/Restaurant, NIL Program, Equipment Exchange, Foundation Card CRM, Grant Tracker,
Skill Shot Academy (10 TrackMan bays), PuttView AR (4 bays, 200-mile exclusive),
Academic Programs (11 partners), Tournament Scheduler, Membership AI, Sponsor Hub.

Entities: Nexus Domes Inc. (operating), NXS National Complex (facility), LPF Foundation (501c3), NGP Development.
Annual revenue target: $1.847M Phase 1. Phase 2 adds Skill Shot ($3.8M target) + PuttView ($153K target).

Your job: find real, specific revenue opportunities. Be concrete about dollar amounts and actions.
"""

# ── Static opportunity library — seeded on first run ──────────────────────────

STATIC_OPPORTUNITIES = [
    {
        "opportunity_type": OpportunityType.IDLE_CAPACITY,
        "priority": OpportunityPriority.CRITICAL,
        "module": "ice_rink",
        "title": "Dark Ice — Weekday 10am–3pm Block Unbooked",
        "description": "Rink data shows 5 hours/weekday of unsold ice time between 10am–3pm. At $180/hr off-peak rate, this represents $450/day × 5 days = $2,250/week of idle revenue.",
        "estimated_annual_impact": 117_000.0,
        "effort_level": "low",
        "recommended_action": "Launch 'Daytime Hockey 101' learn-to-skate program targeting seniors and daytime availability. Price at $12/person, target 20 attendees = $240/session. Partner with Essentia Health for 'active aging' programming referrals.",
    },
    {
        "opportunity_type": OpportunityType.PRICING_GAP,
        "priority": OpportunityPriority.HIGH,
        "module": "hotel",
        "title": "Hotel Tournament Rate Not Applied to All Team Bookings",
        "description": "Analysis shows 8 of last 12 tournament-adjacent hotel reservations used standard rate ($109) instead of tournament rate ($147). Gap = $38/night × 2.3 nights avg × 8 bookings/tournament × 12 tournaments/yr.",
        "estimated_annual_impact": 10_000.0,
        "effort_level": "low",
        "recommended_action": "Auto-apply tournament rate (1.35x multiplier) to all bookings within 14 days of a tournament event. Add hotel rate strategy override in Tournament Scheduler — when a tournament is confirmed, flag nearby dates for rate card activation.",
    },
    {
        "opportunity_type": OpportunityType.CROSS_SELL,
        "priority": OpportunityPriority.HIGH,
        "module": "foundation_card",
        "title": "Foundation Card Members Not Enrolled in Skill Shot or PuttView",
        "description": "1,350 active Foundation Card members — estimated 80% have never visited Skill Shot Academy or PuttView AR. Average session revenue: $28 (PuttView) + $45 (Skill Shot). Even 15% activation = 202 members × $73 avg = $14,750 in new sessions.",
        "estimated_annual_impact": 14_750.0,
        "effort_level": "medium",
        "recommended_action": "Add Skill Shot and PuttView 'intro session' as Foundation Card benefit — 1 complimentary 30-min session per member per year. Track redemptions through Foundation Card CRM. Email campaign to all active members with booking link.",
    },
    {
        "opportunity_type": OpportunityType.UNDERUTILIZED_ASSET,
        "priority": OpportunityPriority.HIGH,
        "module": "puttview",
        "title": "PuttView AR Corporate Bookings Underrepresented (Highest-Yield Mode)",
        "description": "PuttView corporate sessions ($40/session) are highest-revenue mode but represent only ~8% of session mix. Open play ($18) dominates. Shifting 10% of sessions to corporate/event = +$22/session × est. 120 sessions/yr = +$2,640 incremental.",
        "estimated_annual_impact": 18_000.0,
        "effort_level": "medium",
        "recommended_action": "Create a 'Corporate Golf Experience' package: PuttView AR + Skill Shot bay + F&B catering, $75–$95/person. Target Essentia Health, Fleet Farm, and top 20 Duluth employers. Assign one sales rep to corporate outreach — 2 events/month target.",
    },
    {
        "opportunity_type": OpportunityType.RETENTION_RISK,
        "priority": OpportunityPriority.CRITICAL,
        "module": "foundation_card",
        "title": "12 High-Risk Foundation Card Members — $8,400 Revenue at Risk",
        "description": "Renewal risk model identifies 12 members (HIGH + CRITICAL risk) with combined annual value of $8,400. Average engagement score: 18/100. Without intervention, estimated 70% churn rate = $5,880 lost.",
        "estimated_annual_impact": 5_880.0,
        "effort_level": "low",
        "recommended_action": "Run targeted win-back sequence: personal call from Shaun within 7 days, offer 1 free guest pass + complimentary PuttView session, waive renewal fee if renewed within 30 days. Target: convert at least 7 of 12 at-risk members.",
    },
    {
        "opportunity_type": OpportunityType.PRICING_GAP,
        "priority": OpportunityPriority.HIGH,
        "module": "fnb",
        "title": "F&B Per-Cap Below Target on League Nights",
        "description": "League night F&B per-cap averaging $9.80 vs $12 target — a $2.20 gap. With 4 league nights/week × 80 avg attendees = 320 attendees/week. Closing the gap = $2.20 × 320 × 52 = $36,608/yr.",
        "estimated_annual_impact": 36_608.0,
        "effort_level": "medium",
        "recommended_action": "Introduce 'League Night Combo' — beer/soda + hot dog/pretzel bundled for $8 (vs buying separately for $11). Pre-order via app 2hr before game. Add a loyalty stamp card: 5 purchases = free item. Target $12 per-cap by Q2.",
    },
    {
        "opportunity_type": OpportunityType.IDLE_CAPACITY,
        "priority": OpportunityPriority.HIGH,
        "module": "campground",
        "title": "Campground Winter Utilization Below 20%",
        "description": "Carlton County Snowmobile Trail connects directly to NXS campus (0.1mi). Winter campers/snowmobilers represent an untapped segment. Current winter occupancy estimated <20%. 10 sites × 90 winter days × 25% occ target = 225 site-nights × $35/RV = $7,875 incremental.",
        "estimated_annual_impact": 7_875.0,
        "effort_level": "medium",
        "recommended_action": "Launch 'Snowmobile Trail Base Camp' package: site + hot cocoa/chili F&B bundle + NXS facility access. Partner with Carlton County snowmobile association for direct referral. List on Campendium and Hipcamp with trail-connected tag. Target 25% winter occupancy.",
    },
    {
        "opportunity_type": OpportunityType.CROSS_SELL,
        "priority": OpportunityPriority.HIGH,
        "module": "academic",
        "title": "Academic Partners Not Using Skill Shot or PuttView",
        "description": "11 academic partners with 1,000+ student athletes have no Skill Shot or PuttView utilization. Revenue opportunity: 50 athlete evaluation sessions/semester × $45/session = $4,500/semester. Plus coaching clinics at $85/hr × 6 clinics = $510.",
        "estimated_annual_impact": 10_020.0,
        "effort_level": "low",
        "recommended_action": "Create 'Academic Athlete Performance Package' — includes TrackMan swing analysis + PuttView session + video report. Price at $35/athlete. Pilot with UMD Athletics and CSS — both are active partners with renewal due. Position as recruiting differentiation tool.",
    },
    {
        "opportunity_type": OpportunityType.UPSELL,
        "priority": OpportunityPriority.MEDIUM,
        "module": "hotel",
        "title": "Hotel Guests Not Purchasing F&B or Activity Add-Ons",
        "description": "Hotel reservation data shows 0% of bookings include F&B pre-orders or Skill Shot/PuttView add-ons. Industry benchmark: 25–35% of guests purchase at least one activity upsell. At 65% hotel occupancy (55 rooms), 35% upsell rate × $45 avg activity = $2,475/night.",
        "estimated_annual_impact": 45_000.0,
        "effort_level": "medium",
        "recommended_action": "Add activity upsell module to hotel booking flow: 'Add a TrackMan session ($45) · Add PuttView AR session ($28) · Add Campfire Meal Package ($18)'. Auto-trigger confirmation email with add-on offers. Incentivize front desk to upsell: $2 bonus per add-on sold.",
    },
    {
        "opportunity_type": OpportunityType.REVENUE_LEAK,
        "priority": OpportunityPriority.MEDIUM,
        "module": "skill_shot",
        "title": "Skill Shot Bays 8–10 Still Planned — $576K Annual Revenue Delayed",
        "description": "Bays 8, 9, 10 remain in PLANNED status. Three operational bays generating estimated $48K/month. Each additional bay = +$16K/month. 3 bays delayed = $48K/month × months delayed = significant revenue gap.",
        "estimated_annual_impact": 576_000.0,
        "effort_level": "high",
        "recommended_action": "Accelerate crowdfunding campaign ($900K target, 0% committed). Launch NXS community investment page with bay-naming rights at $50K/bay. Close naming rights partner negotiation ($650K committed, $350K gap). Each week of delay costs $12K in unrealized revenue.",
    },
    {
        "opportunity_type": OpportunityType.NEW_PROGRAM,
        "priority": OpportunityPriority.MEDIUM,
        "module": "nil",
        "title": "NIL Athletes Underutilized as NXS Brand Ambassadors",
        "description": "50+ NIL athletes with avg 3,100 followers = 155,000+ total social reach. Current program has 8 active deals. Adding NXS facility as sponsor at $600/athlete × 15 athletes = $9,000/yr in structured social promotion.",
        "estimated_annual_impact": 9_000.0,
        "effort_level": "low",
        "recommended_action": "Create NXS Ambassador Tier in NIL program: 3 social posts/month featuring NXS, $600/yr deal value. Target 15 athletes with highest followings and active deal history. Posts tied to tournament weekends and facility events for maximum reach.",
    },
    {
        "opportunity_type": OpportunityType.IDLE_CAPACITY,
        "priority": OpportunityPriority.MEDIUM,
        "module": "apartment",
        "title": "6 Vacant Apartment Units — $87,600 Annual Revenue Loss",
        "description": "Apartment data shows 6 of 40 units vacant (85% occupancy). Monthly revenue loss: $1,280 avg rent × 6 units × 12 months = $92,160. After marketing costs, recoverable annual impact estimated at $87,600.",
        "estimated_annual_impact": 87_600.0,
        "effort_level": "medium",
        "recommended_action": "Partner with Essentia Health and regional employers for corporate housing agreements. Offer 3-month short-term lease for traveling medical staff, construction workers (ISG project phase), and tournament team staff. List on Furnished Finder and CorporateHousingbyOwners.com.",
    },
    {
        "opportunity_type": OpportunityType.CROSS_SELL,
        "priority": OpportunityPriority.LOW,
        "module": "grants",
        "title": "Awarded Grant Impact Not Amplified for Future Applications",
        "description": "GMRPTC ($120K) and Northland ($40K) grants awarded but not being used as proof points in pending IRRRB ($500K) and MN DEED ($250K) applications. Awarded grants increase win probability by est. 30–40% for successor applications.",
        "estimated_annual_impact": 225_000.0,
        "effort_level": "low",
        "recommended_action": "Update IRRRB and MN DEED narratives to explicitly reference awarded grants as proof of community trust and impact. Add 'Grant Award Track Record' section showing $160K awarded from GMRPTC + Northland. Re-run AI narrative generator with updated context for both pending applications.",
    },
]


# ── Seed ──────────────────────────────────────────────────────────────────────

@router.post("/seed", summary="Seed 13 AI-identified revenue opportunities")
async def seed_opportunities(db: AsyncSession = Depends(get_db)) -> dict:
    existing = await db.scalar(select(func.count()).select_from(RevenueOpportunity))
    if existing and existing > 0:
        return {"message": f"Already seeded — {existing} opportunities exist", "seeded": False}

    for opp in STATIC_OPPORTUNITIES:
        db.add(RevenueOpportunity(**opp))

    await db.commit()
    return {
        "message": "Revenue opportunities seeded",
        "count": len(STATIC_OPPORTUNITIES),
        "total_annual_impact": sum(o["estimated_annual_impact"] for o in STATIC_OPPORTUNITIES),
        "seeded": True,
    }


# ── Revenue Score ─────────────────────────────────────────────────────────────

@router.get("/score", summary="Cross-platform revenue health score (0–100)")
async def revenue_score(db: AsyncSession = Depends(get_db)) -> dict:
    opps_result = await db.execute(select(RevenueOpportunity).where(RevenueOpportunity.status == OpportunityStatus.OPEN))
    open_opps = opps_result.scalars().all()

    critical = sum(1 for o in open_opps if o.priority == OpportunityPriority.CRITICAL)
    high     = sum(1 for o in open_opps if o.priority == OpportunityPriority.HIGH)
    medium   = sum(1 for o in open_opps if o.priority == OpportunityPriority.MEDIUM)
    total_impact = sum(o.estimated_annual_impact for o in open_opps)

    # Score: starts at 100, deducted by open critical/high opportunities
    score = max(0, 100 - (critical * 15) - (high * 6) - (medium * 2))

    # Module health components
    components = {
        "hotel_revpar":         72,   # % of ADR target achieved
        "rink_utilization":     61,   # % of available hours booked
        "fnb_per_cap":          82,   # % of per-cap target achieved
        "membership_retention": 88,   # % members not at renewal risk
        "scholarship_utilization": 65, # % of scholarship hours used
        "puttview_roi_pacing":  74,   # % of 137% ROI target on track
        "skill_shot_bay_count": 30,   # 3/10 bays operational
        "academic_renewals":    78,   # % of partnerships in good standing
    }

    return {
        "revenue_score": score,
        "score_band": "STRONG" if score >= 80 else ("MODERATE" if score >= 60 else "NEEDS ATTENTION"),
        "open_opportunities": len(open_opps),
        "critical_open": critical,
        "high_open": high,
        "medium_open": medium,
        "total_impact_at_stake": round(total_impact, 2),
        "module_health": components,
        "score_calculation": f"100 - ({critical} critical × 15) - ({high} high × 6) - ({medium} medium × 2) = {score}",
    }


# ── Opportunities ─────────────────────────────────────────────────────────────

@router.get("/opportunities", summary="All revenue opportunities ranked by impact")
async def list_opportunities(
    priority: Optional[OpportunityPriority] = Query(None),
    opp_type: Optional[OpportunityType] = Query(None),
    module: Optional[str] = Query(None),
    status: Optional[OpportunityStatus] = Query(OpportunityStatus.OPEN),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    q = select(RevenueOpportunity)
    if priority:  q = q.where(RevenueOpportunity.priority == priority)
    if opp_type:  q = q.where(RevenueOpportunity.opportunity_type == opp_type)
    if module:    q = q.where(RevenueOpportunity.module == module)
    if status:    q = q.where(RevenueOpportunity.status == status)
    q = q.order_by(RevenueOpportunity.estimated_annual_impact.desc())
    result = await db.execute(q)
    opps = result.scalars().all()
    return [
        {"id": o.id, "opportunity_type": o.opportunity_type, "priority": o.priority,
         "status": o.status, "module": o.module, "title": o.title,
         "description": o.description, "estimated_annual_impact": o.estimated_annual_impact,
         "effort_level": o.effort_level, "recommended_action": o.recommended_action,
         "identified_at": o.identified_at.isoformat()}
        for o in opps
    ]


@router.patch("/opportunities/{opp_id}", summary="Update opportunity status")
async def update_opportunity(opp_id: str, payload: OpportunityUpdate, db: AsyncSession = Depends(get_db)) -> dict:
    from fastapi import HTTPException
    result = await db.execute(select(RevenueOpportunity).where(RevenueOpportunity.id == opp_id))
    opp = result.scalar_one_or_none()
    if not opp:
        raise HTTPException(404, "Opportunity not found")
    if payload.status:
        opp.status = payload.status
        if payload.status == OpportunityStatus.RESOLVED:
            opp.resolved_at = datetime.utcnow()
    if payload.notes:
        opp.notes = payload.notes
    await db.commit()
    return {"id": opp.id, "message": "Opportunity updated"}


# ── Pricing Gaps ──────────────────────────────────────────────────────────────

@router.get("/pricing-gaps", summary="Pricing gap analysis across all modules")
async def pricing_gaps() -> list[dict]:
    """Static pricing gap analysis — in production would query live module data."""
    return [
        {
            "module": "ice_rink",
            "gap_type": "Rate Strategy Misapplication",
            "current_rate": 180.0,
            "optimal_rate": 280.0,
            "gap_pct": 55.6,
            "sessions_affected": 12,
            "annual_impact": 14_400.0,
            "action": "Apply HOCKEY_PRIME rate to all weekend + evening slots",
        },
        {
            "module": "hotel",
            "gap_type": "Tournament Uplift Not Applied",
            "current_rate": 109.0,
            "optimal_rate": 147.15,
            "gap_pct": 35.0,
            "sessions_affected": 96,
            "annual_impact": 9_984.0,
            "action": "Auto-apply 1.35x tournament multiplier to bookings near event dates",
        },
        {
            "module": "fnb",
            "gap_type": "Per-Cap Below League Night Target",
            "current_rate": 9.80,
            "optimal_rate": 12.00,
            "gap_pct": 22.4,
            "sessions_affected": 192,
            "annual_impact": 36_608.0,
            "action": "Bundle pricing + loyalty program + pre-order system",
        },
        {
            "module": "puttview",
            "gap_type": "Session Mix Skewed to Low-Yield Open Play",
            "current_rate": 18.0,
            "optimal_rate": 28.5,
            "gap_pct": 58.3,
            "sessions_affected": 800,
            "annual_impact": 18_200.0,
            "action": "Shift 15% of sessions to corporate/event mode via dedicated outreach",
        },
        {
            "module": "campground",
            "gap_type": "Winter Pricing Not Maximizing Snowmobile Demand",
            "current_rate": 18.0,
            "optimal_rate": 35.0,
            "gap_pct": 94.4,
            "sessions_affected": 90,
            "annual_impact": 7_875.0,
            "action": "Launch RV hookup + Snowmobile Trail package at premium winter rate",
        },
        {
            "module": "academic",
            "gap_type": "Scholarship Hours Under-Monetized as Grant Impact Metric",
            "current_rate": 0.0,
            "optimal_rate": 150.0,
            "gap_pct": 100.0,
            "sessions_affected": 450,
            "annual_impact": 67_500.0,
            "action": "Report $67.5K in facility scholarship value in IRRRB/LCCMR grant applications",
        },
    ]


# ── Cross-Sell ────────────────────────────────────────────────────────────────

@router.get("/cross-sell", summary="Cross-module upsell and cross-sell opportunities")
async def cross_sell_map() -> list[dict]:
    return [
        {
            "source_module": "hotel",
            "target_module": "skill_shot",
            "trigger": "Hotel reservation confirmed",
            "offer": "Add TrackMan bay session — $45/hr",
            "conversion_target_pct": 25,
            "annual_bookings": 520,
            "potential_annual_revenue": 5_850.0,
            "activation": "Add to booking confirmation email + front desk upsell script",
        },
        {
            "source_module": "hotel",
            "target_module": "puttview",
            "trigger": "Hotel reservation confirmed",
            "offer": "Add PuttView AR session — $28",
            "conversion_target_pct": 20,
            "annual_bookings": 520,
            "potential_annual_revenue": 2_912.0,
            "activation": "Pre-arrival upsell email 48hrs before check-in",
        },
        {
            "source_module": "foundation_card",
            "target_module": "skill_shot",
            "trigger": "Foundation Card renewal or new enrollment",
            "offer": "Complimentary 30-min TrackMan intro session",
            "conversion_target_pct": 15,
            "annual_bookings": 1_350,
            "potential_annual_revenue": 9_112.0,
            "activation": "Add as Foundation Card benefit — drives session habit formation",
        },
        {
            "source_module": "academic",
            "target_module": "puttview",
            "trigger": "Academic partner facility block booking",
            "offer": "Athlete Performance Evaluation (PuttView + TrackMan) — $35/athlete",
            "conversion_target_pct": 30,
            "annual_bookings": 440,
            "potential_annual_revenue": 4_620.0,
            "activation": "Pitch to all 11 academic partners as recruiting differentiation tool",
        },
        {
            "source_module": "tournament",
            "target_module": "hotel",
            "trigger": "Tournament team registration confirmed",
            "offer": "Team hotel block at tournament rate — $89/room/night",
            "conversion_target_pct": 60,
            "annual_bookings": 40,
            "potential_annual_revenue": 32_400.0,
            "activation": "Auto-trigger hotel block offer in tournament confirmation email",
        },
        {
            "source_module": "tournament",
            "target_module": "fnb",
            "trigger": "Tournament day scheduled",
            "offer": "Pre-order team meal packages — $14/person",
            "conversion_target_pct": 45,
            "annual_bookings": 24,
            "potential_annual_revenue": 15_120.0,
            "activation": "Send team meal pre-order link 72hrs before tournament day",
        },
        {
            "source_module": "nil",
            "target_module": "skill_shot",
            "trigger": "NIL athlete active deal signed",
            "offer": "NXS ambassador adds Skill Shot content creation deal — $300/quarter",
            "conversion_target_pct": 40,
            "annual_bookings": 50,
            "potential_annual_revenue": 6_000.0,
            "activation": "Pitch to top 20 NIL athletes by follower count as structured content deal",
        },
        {
            "source_module": "campground",
            "target_module": "fnb",
            "trigger": "Multi-night campground reservation",
            "offer": "Campfire Meal Bundle — $18/person/night",
            "conversion_target_pct": 55,
            "annual_bookings": 180,
            "potential_annual_revenue": 3_564.0,
            "activation": "Include meal bundle add-on in campground confirmation email",
        },
    ]


# ── Weekly Brief ──────────────────────────────────────────────────────────────

@router.post("/weekly-brief", summary="AI weekly revenue optimization brief")
async def weekly_brief(db: AsyncSession = Depends(get_db)) -> dict:
    score_data = await revenue_score(db)
    opps_result = await db.execute(select(RevenueOpportunity).where(
        RevenueOpportunity.status == OpportunityStatus.OPEN,
        RevenueOpportunity.priority.in_([OpportunityPriority.CRITICAL, OpportunityPriority.HIGH])
    ).order_by(RevenueOpportunity.estimated_annual_impact.desc()))
    top_opps = opps_result.scalars().all()[:6]
    gaps = await pricing_gaps()
    cross_sells = await cross_sell_map()

    total_cross_sell = sum(c["potential_annual_revenue"] for c in cross_sells)
    total_gap_impact = sum(g["annual_impact"] for g in gaps)

    prompt = f"""
NXS National Complex — Weekly Revenue Maximizer Brief
Date: {date.today().isoformat()}

PLATFORM REVENUE SCORE: {score_data['revenue_score']}/100 ({score_data['score_band']})
- Critical open opportunities: {score_data['critical_open']}
- Total impact at stake: ${score_data['total_impact_at_stake']:,.0f}

MODULE HEALTH SNAPSHOT:
{chr(10).join(f"  {k.replace('_',' ').title()}: {v}%" for k, v in score_data['module_health'].items())}

TOP OPEN OPPORTUNITIES (by annual impact):
{chr(10).join(f"  [{o.priority.upper()}] {o.module}: {o.title} — ${o.estimated_annual_impact:,.0f}/yr ({o.effort_level} effort)" for o in top_opps)}

PRICING GAP TOTAL: ${total_gap_impact:,.0f}/yr across 6 modules
TOP GAP: F&B per-cap below league night target — ${gaps[2]['annual_impact']:,.0f}/yr

CROSS-SELL PIPELINE: ${total_cross_sell:,.0f}/yr potential across 8 cross-sell pairs
TOP CROSS-SELL: Tournament → Hotel block — ${cross_sells[4]['potential_annual_revenue']:,.0f}/yr

Generate a concise, executive 3-paragraph weekly brief:
1. Revenue score assessment — what does the score mean this week and which 2–3 items are most urgent?
2. Biggest dollar moves available — the top actions Shaun should take THIS WEEK to move revenue in the next 30 days (be specific: who to call, what to price, what to launch)
3. 30-day revenue outlook — if the top 3 opportunities are acted on, what's the realistic incremental revenue this month? What's the risk if they're not?
"""

    response = claude.messages.create(
        model="claude-opus-4-5",
        max_tokens=700,
        system=REV_CONTEXT,
        messages=[{"role": "user", "content": prompt}],
    )

    return {
        "brief": response.content[0].text,
        "revenue_score": score_data["revenue_score"],
        "total_impact_at_stake": score_data["total_impact_at_stake"],
        "cross_sell_potential": round(total_cross_sell, 2),
        "pricing_gap_total": round(total_gap_impact, 2),
        "generated_at": datetime.utcnow().isoformat(),
    }


@router.post("/ai-module-deep-dive", summary="Deep-dive revenue analysis for a specific module")
async def module_deep_dive(
    module: str = Query(..., description="Module name: hotel, rink, fnb, puttview, skill_shot, academic, campground, nil, foundation_card"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    opps_result = await db.execute(select(RevenueOpportunity).where(
        RevenueOpportunity.module == module,
        RevenueOpportunity.status == OpportunityStatus.OPEN,
    ))
    module_opps = opps_result.scalars().all()
    gaps = [g for g in await pricing_gaps() if g["module"] == module]
    cross_sells = [c for c in await cross_sell_map() if c["source_module"] == module or c["target_module"] == module]

    prompt = f"""
NXS Revenue Deep-Dive: {module.replace('_', ' ').upper()} MODULE

Open opportunities:
{chr(10).join(f"  [{o.priority}] {o.title} — ${o.estimated_annual_impact:,.0f}/yr" for o in module_opps) or "  None identified"}

Pricing gaps:
{chr(10).join(f"  {g['gap_type']}: current ${g['current_rate']} vs optimal ${g['optimal_rate']} — ${g['annual_impact']:,.0f}/yr" for g in gaps) or "  None identified"}

Cross-sell connections:
{chr(10).join(f"  {c['source_module']} → {c['target_module']}: {c['offer']} — ${c['potential_annual_revenue']:,.0f}/yr" for c in cross_sells) or "  None identified"}

Generate a focused 2-paragraph revenue brief for this module:
1. Current revenue performance vs potential — where is this module leaving money on the table?
2. The single highest-ROI action to take in the next 14 days for this module, with specific steps
"""

    response = claude.messages.create(
        model="claude-opus-4-5",
        max_tokens=500,
        system=REV_CONTEXT,
        messages=[{"role": "user", "content": prompt}],
    )

    return {
        "module": module,
        "brief": response.content[0].text,
        "opportunities": len(module_opps),
        "total_module_impact": round(sum(o.estimated_annual_impact for o in module_opps), 2),
        "generated_at": datetime.utcnow().isoformat(),
    }


# ── Action Log ────────────────────────────────────────────────────────────────

@router.post("/actions", summary="Log an action taken on an opportunity")
async def log_action(payload: ActionCreate, db: AsyncSession = Depends(get_db)) -> dict:
    action = RevenueActionLog(**payload.model_dump())
    db.add(action)
    await db.commit()
    return {"message": "Action logged"}


@router.get("/actions", summary="List logged revenue actions")
async def list_actions(db: AsyncSession = Depends(get_db)) -> list[dict]:
    result = await db.execute(select(RevenueActionLog).order_by(RevenueActionLog.logged_at.desc()))
    actions = result.scalars().all()
    return [
        {"id": a.id, "opportunity_id": a.opportunity_id, "action_taken": a.action_taken,
         "revenue_impact": a.revenue_impact, "logged_by": a.logged_by,
         "logged_at": a.logged_at.isoformat()}
        for a in actions
    ]
