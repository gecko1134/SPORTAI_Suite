"""
SportAI Suite — Facility Layout Optimizer
Sprint 7 · NXS National Complex
171,700 sqft Large Dome · 36,100 sqft Small Dome · 15,700 sqft Health Center
Outdoor fields, rink, campground, hotel, parking
Space utilization heatmaps · Revenue per sqft · Configuration scenarios · AI optimization

Add to main.py:
    from routers.layout_ai import router as layout_router
    app.include_router(layout_router)
"""

from __future__ import annotations

import enum
import uuid
from datetime import date, datetime, timedelta
from typing import Optional
import random

from anthropic import Anthropic
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import (
    Boolean, DateTime, Enum as SAEnum, Float, Integer, String, Text, func, select
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


# ── Campus constants ──────────────────────────────────────────────────────────

CAMPUS_ZONES = [
    # Large Dome
    {"zone_id": "LD-TURF-FULL",  "name": "Large Dome — Full Turf Field",   "area": "large_dome",       "sqft": 171_700, "primary_use": "soccer/lacrosse/football",   "hourly_rate": 200.0, "capacity": 1_500},
    {"zone_id": "LD-TURF-HALF1", "name": "Large Dome — Turf Half-Field A", "area": "large_dome",       "sqft": 85_850,  "primary_use": "soccer/lacrosse",             "hourly_rate": 120.0, "capacity": 750},
    {"zone_id": "LD-TURF-HALF2", "name": "Large Dome — Turf Half-Field B", "area": "large_dome",       "sqft": 85_850,  "primary_use": "soccer/lacrosse",             "hourly_rate": 120.0, "capacity": 750},
    {"zone_id": "LD-BB-A",       "name": "Large Dome — Basketball Court A", "area": "large_dome",      "sqft": 5_700,   "primary_use": "basketball",                  "hourly_rate": 80.0,  "capacity": 200},
    {"zone_id": "LD-BB-B",       "name": "Large Dome — Basketball Court B", "area": "large_dome",      "sqft": 5_700,   "primary_use": "basketball",                  "hourly_rate": 80.0,  "capacity": 200},
    {"zone_id": "LD-VB-A",       "name": "Large Dome — Volleyball Court A", "area": "large_dome",      "sqft": 4_500,   "primary_use": "volleyball",                  "hourly_rate": 70.0,  "capacity": 150},
    {"zone_id": "LD-VB-B",       "name": "Large Dome — Volleyball Court B", "area": "large_dome",      "sqft": 4_500,   "primary_use": "volleyball",                  "hourly_rate": 70.0,  "capacity": 150},
    # Small Dome
    {"zone_id": "SD-TURF",       "name": "Small Dome — Turf Field",         "area": "small_dome",      "sqft": 36_100,  "primary_use": "multi-sport/training",        "hourly_rate": 120.0, "capacity": 400},
    {"zone_id": "SD-SKILL-SHOT", "name": "Small Dome — Skill Shot Academy", "area": "small_dome",      "sqft": 8_000,   "primary_use": "trackman_bays",               "hourly_rate": 45.0,  "capacity": 40},
    {"zone_id": "SD-PUTTVIEW",   "name": "Small Dome — PuttView AR Bays",  "area": "small_dome",      "sqft": 2_400,   "primary_use": "puttview_ar",                 "hourly_rate": 18.0,  "capacity": 16},
    # Health Center
    {"zone_id": "HC-GYM",        "name": "Health Center — Fitness Gym",    "area": "health_center",   "sqft": 8_500,   "primary_use": "fitness/training",            "hourly_rate": 15.0,  "capacity": 120},
    {"zone_id": "HC-COURTS",     "name": "Health Center — Pickleball Courts","area": "health_center",  "sqft": 4_200,   "primary_use": "pickleball",                  "hourly_rate": 25.0,  "capacity": 40},
    {"zone_id": "HC-CLINIC",     "name": "Health Center — Sports Medicine Clinic","area": "health_center","sqft": 3_000,"primary_use": "medical/therapy",             "hourly_rate": 0.0,   "capacity": 30},
    # Outdoor
    {"zone_id": "OUT-SOCCER1",   "name": "Outdoor Soccer Field 1 (195×330)", "area": "outdoor",        "sqft": 64_350,  "primary_use": "soccer/lacrosse",             "hourly_rate": 80.0,  "capacity": 500},
    {"zone_id": "OUT-SOCCER2",   "name": "Outdoor Soccer Field 2 (195×330)", "area": "outdoor",        "sqft": 64_350,  "primary_use": "soccer/lacrosse",             "hourly_rate": 80.0,  "capacity": 500},
    # Special
    {"zone_id": "ICE-RINK",      "name": "Ice Rink (200×85 NHL)",           "area": "rink",            "sqft": 17_000,  "primary_use": "hockey/skating",              "hourly_rate": 220.0, "capacity": 500},
    {"zone_id": "CAMP-SITES",    "name": "Campground (30 sites)",           "area": "campground",      "sqft": 45_000,  "primary_use": "camping/recreation",          "hourly_rate": 0.0,   "capacity": 180},
    {"zone_id": "HOTEL",         "name": "Hotel (85 units)",                "area": "hotel",           "sqft": 72_000,  "primary_use": "lodging",                     "hourly_rate": 0.0,   "capacity": 170},
    {"zone_id": "PARKING",       "name": "Parking (1,656 stalls)",          "area": "parking",         "sqft": 600_000, "primary_use": "parking",                     "hourly_rate": 0.0,   "capacity": 6_000},
]

ZONE_IDS = {z["zone_id"] for z in CAMPUS_ZONES}
TOTAL_INDOOR_SQFT = 171_700 + 36_100 + 15_700   # 223,500
TOTAL_CAMPUS_SQFT = sum(z["sqft"] for z in CAMPUS_ZONES)


class FacilityZone(Base):
    """NXS campus zone with utilization tracking."""
    __tablename__ = "facility_zones"

    id: Mapped[str]              = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    zone_id: Mapped[str]         = mapped_column(String(20), nullable=False, unique=True)
    name: Mapped[str]            = mapped_column(String(200), nullable=False)
    area: Mapped[str]            = mapped_column(String(50), nullable=False)
    sqft: Mapped[int]            = mapped_column(Integer, nullable=False)
    primary_use: Mapped[str]     = mapped_column(String(100), nullable=False)
    hourly_rate: Mapped[float]   = mapped_column(Float, nullable=False)
    capacity: Mapped[int]        = mapped_column(Integer, nullable=False)
    # Live utilization
    utilization_pct: Mapped[float]    = mapped_column(Float, default=0.0)   # 0–100
    revenue_per_sqft_annual: Mapped[float] = mapped_column(Float, default=0.0)
    peak_hours: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    notes: Mapped[Optional[str]]      = mapped_column(Text, nullable=True)
    is_active: Mapped[bool]           = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime]      = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime]      = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class LayoutScenario(Base):
    """Alternative layout configuration for revenue comparison."""
    __tablename__ = "layout_scenarios"

    id: Mapped[str]              = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str]            = mapped_column(String(200), nullable=False)
    description: Mapped[str]     = mapped_column(Text, nullable=False)
    zone_changes: Mapped[str]    = mapped_column(Text, nullable=False)    # JSON-like description
    projected_revenue_change: Mapped[float] = mapped_column(Float, nullable=False)
    revenue_change_pct: Mapped[float]       = mapped_column(Float, nullable=False)
    implementation_cost: Mapped[float]      = mapped_column(Float, default=0.0)
    payback_months: Mapped[Optional[int]]   = mapped_column(Integer, nullable=True)
    pros: Mapped[str]            = mapped_column(Text, nullable=False)
    cons: Mapped[str]            = mapped_column(Text, nullable=False)
    status: Mapped[str]          = mapped_column(String(20), default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SpaceUtilizationSnapshot(Base):
    """Weekly utilization snapshot per zone — historical tracking."""
    __tablename__ = "space_utilization_snapshots"

    id: Mapped[str]              = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    zone_id: Mapped[str]         = mapped_column(String(20), nullable=False)
    week_of: Mapped[date]        = mapped_column(DateTime, nullable=False)
    utilization_pct: Mapped[float] = mapped_column(Float, nullable=False)
    hours_booked: Mapped[float]  = mapped_column(Float, nullable=False)
    revenue: Mapped[float]       = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# ── DB dependency ─────────────────────────────────────────────────────────────

async def get_db() -> AsyncSession:
    raise NotImplementedError("Replace with: from database import get_db  # then remove this function")


# ── Router ────────────────────────────────────────────────────────────────────

router = APIRouter(prefix="/api/layout-ai", tags=["Facility Layout Optimizer"])
claude = Anthropic()

LAYOUT_CONTEXT = """
You are the AI facility layout optimizer for NXS National Complex, Proctor MN.
Campus: Large Dome 171,700 sqft | Small Dome 36,100 sqft | Health Center 15,700 sqft
2 outdoor soccer fields (195×330 each) | Ice Rink 200×85 | Campground | Hotel 85 units | 1,656 parking stalls.
Total indoor: 223,500 sqft. Revenue target: $1.847M Phase 1 + Phase 2 additions.
Optimize for: revenue per sqft, utilization rate, sport mix balance, peak-hour demand.
ISG Engineering Project #24688001. Provide specific, dollar-quantified layout recommendations.
"""


@router.post("/seed", summary="Seed facility zones and utilization data")
async def seed_layout(db: AsyncSession = Depends(get_db)) -> dict:
    existing = await db.scalar(select(func.count()).select_from(FacilityZone))
    if existing and existing > 0:
        return {"message": f"Already seeded — {existing} zones exist", "seeded": False}

    random.seed(42)
    today = date.today()

    # Realistic utilization estimates per zone type
    util_estimates = {
        "LD-TURF-FULL": (72, 285.0), "LD-TURF-HALF1": (58, 91.0), "LD-TURF-HALF2": (54, 84.0),
        "LD-BB-A": (61, 63.0), "LD-BB-B": (55, 57.0), "LD-VB-A": (68, 61.0), "LD-VB-B": (64, 57.0),
        "SD-TURF": (48, 73.0), "SD-SKILL-SHOT": (32, 145.0), "SD-PUTTVIEW": (41, 97.0),
        "HC-GYM": (78, 38.0), "HC-COURTS": (69, 45.0), "HC-CLINIC": (85, 0.0),
        "OUT-SOCCER1": (44, 44.0), "OUT-SOCCER2": (41, 41.0),
        "ICE-RINK": (62, 277.0), "CAMP-SITES": (38, 12.0), "HOTEL": (65, 148.0), "PARKING": (52, 0.0),
    }

    for zone_data in CAMPUS_ZONES:
        zid = zone_data["zone_id"]
        util_pct, rev_sqft = util_estimates.get(zid, (45, 50.0))
        zone = FacilityZone(
            zone_id=zid,
            name=zone_data["name"],
            area=zone_data["area"],
            sqft=zone_data["sqft"],
            primary_use=zone_data["primary_use"],
            hourly_rate=zone_data["hourly_rate"],
            capacity=zone_data["capacity"],
            utilization_pct=float(util_pct) + random.uniform(-5, 5),
            revenue_per_sqft_annual=rev_sqft + random.uniform(-8, 8),
            peak_hours="5pm–10pm weekdays, 8am–6pm weekends" if "Dome" in zone_data["name"] else None,
        )
        db.add(zone)

    # Seed layout scenarios
    scenarios = [
        LayoutScenario(
            name="Expand Skill Shot to 14 Bays",
            description="Convert 4,000 sqft of Small Dome underutilized practice space to 4 additional TrackMan bays. Brings total to 14 operational bays.",
            zone_changes="SD-TURF: -4,000 sqft | SD-SKILL-SHOT: +4,000 sqft (4 additional bays)",
            projected_revenue_change=384_000.0,
            revenue_change_pct=20.8,
            implementation_cost=280_000.0,
            payback_months=9,
            pros="Highest revenue per sqft of any zone. Immediate demand. TrackMan expansion scalable.",
            cons="Reduces turf practice space. 8-week construction period.",
            status="recommended",
        ),
        LayoutScenario(
            name="Convert Large Dome Corner to Pickleball Courts",
            description="Add 4 permanent pickleball courts in Large Dome corners (currently unused during turf events). 6,000 sqft re-purposed.",
            zone_changes="LD-TURF-FULL: -6,000 sqft corner allocation | New: LD-PB-A, LD-PB-B (2 courts each)",
            projected_revenue_change=58_500.0,
            revenue_change_pct=3.2,
            implementation_cost=45_000.0,
            payback_months=10,
            pros="Pickleball fastest-growing sport. Courts revenue 24/7 independent of turf events. Low install cost.",
            cons="Corner courts reduce spectator sightlines for large events. Permanent installation limits flexibility.",
            status="draft",
        ),
        LayoutScenario(
            name="Nighttime Dome Revenue Activation (Esports/Events)",
            description="Lease 20,000 sqft of Large Dome 10pm–2am to esports tournament organizers and late-night events. Currently dark.",
            zone_changes="LD-TURF-FULL: add 10pm–2am revenue block | New: LED setup, seating configuration",
            projected_revenue_change=96_000.0,
            revenue_change_pct=5.2,
            implementation_cost=35_000.0,
            payback_months=4,
            pros="Zero new construction. Uses otherwise dark hours. Esports demographic is 18–35, new audience.",
            cons="Requires security/staffing 10pm–2am. Sound management needed. Community impact consideration.",
            status="draft",
        ),
        LayoutScenario(
            name="Health Center Expansion — Specialty Clinic Suites",
            description="Convert 3,000 sqft of underutilized Health Center space to specialist clinic suites (ortho, sports medicine, PT). Lease to Essentia Health.",
            zone_changes="HC-CLINIC: +3,000 sqft expansion | Essentia Health 5-yr lease at $31,250/mo",
            projected_revenue_change=375_000.0,
            revenue_change_pct=20.3,
            implementation_cost=180_000.0,
            payback_months=6,
            pros="Essentia already leasing base TCO space. Strong demand for sports-adjacent medical care. Recurring NNN lease revenue.",
            cons="Capital required for clinical-grade buildout. Long-term lease reduces flexibility.",
            status="recommended",
        ),
    ]
    for s in scenarios:
        db.add(s)

    # Utilization snapshots — 8 weeks of history
    for week_offset in range(8, 0, -1):
        week_date = today - timedelta(weeks=week_offset)
        for zone_data in CAMPUS_ZONES[:12]:  # Top 12 zones
            snap = SpaceUtilizationSnapshot(
                zone_id=zone_data["zone_id"],
                week_of=week_date,
                utilization_pct=float(util_estimates.get(zone_data["zone_id"], (45, 0))[0]) + random.uniform(-8, 8),
                hours_booked=float(zone_data.get("sqft", 0)) / 10000 * random.uniform(8, 16),
                revenue=zone_data["hourly_rate"] * random.uniform(8, 16) if zone_data["hourly_rate"] > 0 else 0,
            )
            db.add(snap)

    await db.commit()
    return {
        "message": "Facility Layout Optimizer seeded",
        "zones": len(CAMPUS_ZONES),
        "scenarios": len(scenarios),
        "snapshots": 8 * 12,
        "total_campus_sqft": TOTAL_CAMPUS_SQFT,
        "seeded": True,
    }


@router.get("/zones", summary="All campus zones with utilization and revenue metrics")
async def list_zones(
    area: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    q = select(FacilityZone).where(FacilityZone.is_active == True)
    if area:
        q = q.where(FacilityZone.area == area)
    q = q.order_by(FacilityZone.revenue_per_sqft_annual.desc())
    result = await db.execute(q)
    zones = result.scalars().all()
    return [
        {"id": z.id, "zone_id": z.zone_id, "name": z.name, "area": z.area,
         "sqft": z.sqft, "primary_use": z.primary_use, "hourly_rate": z.hourly_rate,
         "capacity": z.capacity, "utilization_pct": round(z.utilization_pct, 1),
         "revenue_per_sqft_annual": round(z.revenue_per_sqft_annual, 2),
         "peak_hours": z.peak_hours}
        for z in zones
    ]


@router.get("/utilization-heatmap", summary="Heatmap data — utilization by zone and hour-of-day")
async def utilization_heatmap(db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(select(FacilityZone).where(FacilityZone.is_active == True))
    zones = result.scalars().all()

    # Synthetic hourly distribution pattern per zone type
    def _hour_pattern(area: str, base_util: float) -> list[float]:
        hrs = []
        for h in range(6, 23):  # 6am–10pm
            if area == "large_dome":
                factor = 0.3 if h < 9 else (0.6 if h < 12 else (0.5 if h < 17 else (1.0 if h < 21 else 0.7)))
            elif area == "rink":
                factor = 0.8 if h < 9 else (0.3 if h < 16 else (1.0 if h < 22 else 0.5))
            elif area == "hotel":
                factor = 0.9  # hotel doesn't have hourly variation — stays ~constant
            else:
                factor = 0.4 if h < 10 else (0.7 if h < 17 else (0.9 if h < 21 else 0.5))
            hrs.append(round(min(100, base_util * factor), 1))
        return hrs

    heatmap = {}
    for z in zones:
        if z.area in ["parking", "outdoor"]:
            continue
        heatmap[z.zone_id] = {
            "name": z.name,
            "area": z.area,
            "hours": list(range(6, 23)),
            "utilization": _hour_pattern(z.area, z.utilization_pct),
            "avg_utilization": round(z.utilization_pct, 1),
            "revenue_per_sqft": round(z.revenue_per_sqft_annual, 2),
        }

    # Summary by area
    area_summary = {}
    for z in zones:
        if z.area not in area_summary:
            area_summary[z.area] = {"zones": 0, "total_sqft": 0, "avg_utilization": [], "total_rev_sqft": []}
        area_summary[z.area]["zones"] += 1
        area_summary[z.area]["total_sqft"] += z.sqft
        area_summary[z.area]["avg_utilization"].append(z.utilization_pct)
        area_summary[z.area]["total_rev_sqft"].append(z.revenue_per_sqft_annual)

    area_rollup = {
        area: {
            "zones": v["zones"],
            "total_sqft": v["total_sqft"],
            "avg_utilization_pct": round(sum(v["avg_utilization"]) / len(v["avg_utilization"]), 1),
            "avg_revenue_per_sqft": round(sum(v["total_rev_sqft"]) / len(v["total_rev_sqft"]), 2),
        }
        for area, v in area_summary.items()
    }

    return {
        "heatmap": heatmap,
        "area_summary": area_rollup,
        "total_indoor_sqft": TOTAL_INDOOR_SQFT,
        "total_campus_sqft": TOTAL_CAMPUS_SQFT,
    }


@router.get("/revenue-per-sqft", summary="Revenue per sqft analysis — ranked by efficiency")
async def revenue_per_sqft(db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(select(FacilityZone).where(FacilityZone.is_active == True).order_by(FacilityZone.revenue_per_sqft_annual.desc()))
    zones = result.scalars().all()

    revenue_zones = [z for z in zones if z.revenue_per_sqft_annual > 0]
    top_performers   = revenue_zones[:5]
    under_performers = sorted(revenue_zones, key=lambda z: z.revenue_per_sqft_annual)[:5]

    total_rev = sum(z.sqft * z.revenue_per_sqft_annual for z in revenue_zones)
    avg_rev_sqft = total_rev / sum(z.sqft for z in revenue_zones) if revenue_zones else 0

    return {
        "avg_revenue_per_sqft_annual": round(avg_rev_sqft, 2),
        "total_estimated_annual_revenue": round(total_rev, 2),
        "top_performers": [
            {"zone_id": z.zone_id, "name": z.name, "sqft": z.sqft,
             "revenue_per_sqft": round(z.revenue_per_sqft_annual, 2),
             "utilization_pct": round(z.utilization_pct, 1),
             "annual_revenue_est": round(z.sqft * z.revenue_per_sqft_annual, 2)}
            for z in top_performers
        ],
        "under_performers": [
            {"zone_id": z.zone_id, "name": z.name, "sqft": z.sqft,
             "revenue_per_sqft": round(z.revenue_per_sqft_annual, 2),
             "utilization_pct": round(z.utilization_pct, 1),
             "gap_to_avg": round(avg_rev_sqft - z.revenue_per_sqft_annual, 2)}
            for z in under_performers
        ],
        "zone_rankings": [
            {"zone_id": z.zone_id, "name": z.name, "area": z.area, "sqft": z.sqft,
             "revenue_per_sqft": round(z.revenue_per_sqft_annual, 2),
             "utilization_pct": round(z.utilization_pct, 1)}
            for z in revenue_zones
        ],
    }


@router.get("/scenarios", summary="Layout configuration scenarios")
async def list_scenarios(db: AsyncSession = Depends(get_db)) -> list[dict]:
    result = await db.execute(select(LayoutScenario).order_by(LayoutScenario.projected_revenue_change.desc()))
    scenarios = result.scalars().all()
    return [
        {"id": s.id, "name": s.name, "description": s.description,
         "zone_changes": s.zone_changes,
         "projected_revenue_change": s.projected_revenue_change,
         "revenue_change_pct": s.revenue_change_pct,
         "implementation_cost": s.implementation_cost,
         "payback_months": s.payback_months,
         "pros": s.pros, "cons": s.cons, "status": s.status}
        for s in scenarios
    ]


@router.post("/ai-optimize", summary="AI facility optimization recommendations")
async def ai_optimize(db: AsyncSession = Depends(get_db)) -> dict:
    rev_data = await revenue_per_sqft(db)
    heatmap_data = await utilization_heatmap(db)
    scenarios = await list_scenarios(db)

    top_5 = rev_data["top_performers"]
    bottom_5 = rev_data["under_performers"]

    top_scenarios_summary = "\n".join(
        f"  {s['name']}: +${s['projected_revenue_change']:,.0f}/yr (+{s['revenue_change_pct']}%), costs ${s['implementation_cost']:,.0f}, payback {s['payback_months']}mo"
        for s in scenarios[:4]
    )

    area_util = "\n".join(
        f"  {area}: {data['avg_utilization_pct']}% avg util | ${data['avg_revenue_per_sqft']}/sqft | {data['total_sqft']:,} sqft"
        for area, data in heatmap_data["area_summary"].items()
    )

    prompt = f"""
NXS National Complex — Facility Layout Optimization Brief
Total indoor: {TOTAL_INDOOR_SQFT:,} sqft | Total campus: {TOTAL_CAMPUS_SQFT:,} sqft

AREA UTILIZATION:
{area_util}

TOP REVENUE GENERATORS ($/sqft/yr):
{chr(10).join(f"  {z['name']}: ${z['revenue_per_sqft']}/sqft, {z['utilization_pct']}% utilized" for z in top_5)}

UNDERPERFORMING ZONES ($/sqft/yr):
{chr(10).join(f"  {z['name']}: ${z['revenue_per_sqft']}/sqft, {z['utilization_pct']}% utilized, gap ${z['gap_to_avg']:.0f}/sqft to avg" for z in bottom_5)}

AVG REVENUE/SQFT: ${rev_data['avg_revenue_per_sqft_annual']:.2f}/yr
TOTAL ESTIMATED ANNUAL REVENUE: ${rev_data['total_estimated_annual_revenue']:,.0f}

CONFIGURATION SCENARIOS:
{top_scenarios_summary}

Generate a 3-paragraph facility optimization brief:
1. Layout efficiency assessment — which zones are working hardest per square foot and which are dragging the average down? Specific dollar gap between best and worst performers.
2. Top 2 layout changes to prioritize — from the scenarios above or new ideas. Include implementation sequence and quick-win vs long-term split.
3. Peak hour dead zones — based on utilization data, which facility areas are dark during prime 5–10pm hours and what specific programs would fill them profitably?
"""

    response = claude.messages.create(
        model="claude-opus-4-5",
        max_tokens=700,
        system=LAYOUT_CONTEXT,
        messages=[{"role": "user", "content": prompt}],
    )

    return {
        "optimization": response.content[0].text,
        "revenue_summary": {
            "avg_revenue_per_sqft": rev_data["avg_revenue_per_sqft_annual"],
            "total_estimated": rev_data["total_estimated_annual_revenue"],
        },
        "top_scenario": scenarios[0] if scenarios else None,
        "generated_at": datetime.utcnow().isoformat(),
    }


@router.post("/ai-scenario-compare", summary="AI comparison of two layout scenarios")
async def ai_scenario_compare(
    scenario_a_id: str = Query(...),
    scenario_b_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
) -> dict:
    from fastapi import HTTPException
    all_scenarios = await list_scenarios(db)
    a = next((s for s in all_scenarios if s["id"] == scenario_a_id), None)
    b = next((s for s in all_scenarios if s["id"] == scenario_b_id), None)
    if not a or not b:
        raise HTTPException(404, "Scenario not found")

    prompt = f"""
Compare these two NXS facility layout scenarios:

SCENARIO A: {a['name']}
Description: {a['description']}
Revenue impact: +${a['projected_revenue_change']:,.0f}/yr (+{a['revenue_change_pct']}%)
Implementation cost: ${a['implementation_cost']:,.0f} | Payback: {a['payback_months']} months
Pros: {a['pros']}
Cons: {a['cons']}

SCENARIO B: {b['name']}
Description: {b['description']}
Revenue impact: +${b['projected_revenue_change']:,.0f}/yr (+{b['revenue_change_pct']}%)
Implementation cost: ${b['implementation_cost']:,.0f} | Payback: {b['payback_months']} months
Pros: {b['pros']}
Cons: {b['cons']}

In 2 paragraphs: (1) Which scenario produces better ROI and why — compare payback periods, revenue per dollar invested, and strategic fit with NXS campus goals.
(2) Can they be sequenced? If so, which first and why — or are they mutually exclusive?
"""

    response = claude.messages.create(
        model="claude-opus-4-5",
        max_tokens=500,
        system=LAYOUT_CONTEXT,
        messages=[{"role": "user", "content": prompt}],
    )

    return {
        "comparison": response.content[0].text,
        "scenario_a": a,
        "scenario_b": b,
        "winner_by_roi": a["name"] if (a["projected_revenue_change"] / max(a["implementation_cost"], 1)) > (b["projected_revenue_change"] / max(b["implementation_cost"], 1)) else b["name"],
        "generated_at": datetime.utcnow().isoformat(),
    }
