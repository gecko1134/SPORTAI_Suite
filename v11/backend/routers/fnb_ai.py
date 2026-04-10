"""
SportAI Suite — F&B / Restaurant Module
Sprint 5 · NXS National Complex
Phase 2 restaurant buildout ($720K) · Event-day revenue tracking
Concession POS · Tournament catering · Food truck plaza ($10–50K sponsorship)
Tournament-correlated revenue model

Add to main.py:
    from routers.fnb_ai import router as fnb_router
    app.include_router(fnb_router)
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
    Boolean, Date, DateTime, Enum as SAEnum,
    Float, ForeignKey, Integer, String, Text, func, select
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# ── Constants ─────────────────────────────────────────────────────────────────

RESTAURANT_BUILDOUT_COST = 720_000.0
FOOD_TRUCK_SPONSORSHIP_RANGE = (10_000.0, 50_000.0)
FOOD_TRUCK_SPOTS = 6      # Plaza spots available
FOOD_TRUCK_DAYS_PER_MONTH = 8   # avg active days

PER_CAP_TARGETS = {
    "tournament_day":   18.0,   # $/attendee on tournament days
    "league_night":     12.0,   # $/attendee on league nights
    "open_event":        9.0,   # $/attendee on general events
    "concession_only":   6.0,   # $/attendee concession-only events
}


# ── Enums ─────────────────────────────────────────────────────────────────────

class VenueType(str, enum.Enum):
    MAIN_RESTAURANT  = "main_restaurant"
    CONCESSION_STAND = "concession_stand"
    FOOD_TRUCK_PLAZA = "food_truck_plaza"
    CATERING_KITCHEN = "catering_kitchen"
    BAR_LOUNGE       = "bar_lounge"


class EventType(str, enum.Enum):
    TOURNAMENT      = "tournament"
    LEAGUE_NIGHT    = "league_night"
    OPEN_EVENT      = "open_event"
    CORPORATE       = "corporate"
    PRIVATE_EVENT   = "private_event"
    CAMP_DAY        = "camp_day"
    OPEN_PLAY       = "open_play"


class FoodTruckStatus(str, enum.Enum):
    SCHEDULED   = "scheduled"
    ACTIVE      = "active"
    COMPLETED   = "completed"
    CANCELLED   = "cancelled"


class CateringStatus(str, enum.Enum):
    INQUIRY    = "inquiry"
    CONFIRMED  = "confirmed"
    COMPLETED  = "completed"
    CANCELLED  = "cancelled"


# ── ORM Models ────────────────────────────────────────────────────────────────

class FnBVenue(Base):
    """F&B venue within the NXS campus."""
    __tablename__ = "fnb_venues"

    id: Mapped[str]               = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str]             = mapped_column(String(200), nullable=False)
    venue_type: Mapped[str]       = mapped_column(SAEnum(VenueType), nullable=False)
    capacity: Mapped[int]         = mapped_column(Integer, nullable=False)
    is_operational: Mapped[bool]  = mapped_column(Boolean, default=False)   # Phase 2 — some not open yet
    phase_open: Mapped[int]       = mapped_column(Integer, default=2)        # 1 or 2
    buildout_cost: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    description: Mapped[Optional[str]]     = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime]           = mapped_column(DateTime(timezone=True), server_default=func.now())

    events: Mapped[list["FnBEvent"]] = relationship("FnBEvent", back_populates="venue", cascade="all, delete-orphan")


class FnBEvent(Base):
    """F&B revenue event — tied to facility activity."""
    __tablename__ = "fnb_events"

    id: Mapped[str]               = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    venue_id: Mapped[str]         = mapped_column(ForeignKey("fnb_venues.id"), nullable=False)
    event_type: Mapped[str]       = mapped_column(SAEnum(EventType), nullable=False)
    title: Mapped[str]            = mapped_column(String(200), nullable=False)
    event_date: Mapped[date]      = mapped_column(Date, nullable=False)
    attendees: Mapped[int]        = mapped_column(Integer, nullable=False)
    per_cap_spend: Mapped[float]  = mapped_column(Float, nullable=False)
    gross_revenue: Mapped[float]  = mapped_column(Float, nullable=False)
    cogs_pct: Mapped[float]       = mapped_column(Float, default=0.32)   # 32% cost of goods
    net_revenue: Mapped[float]    = mapped_column(Float, nullable=False)
    food_truck_revenue: Mapped[float]   = mapped_column(Float, default=0.0)
    catering_revenue: Mapped[float]     = mapped_column(Float, default=0.0)
    sponsor_contribution: Mapped[float] = mapped_column(Float, default=0.0)
    notes: Mapped[Optional[str]]        = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime]        = mapped_column(DateTime(timezone=True), server_default=func.now())

    venue: Mapped["FnBVenue"] = relationship("FnBVenue", back_populates="events")


class FoodTruckSchedule(Base):
    """Food truck plaza scheduling."""
    __tablename__ = "fnb_food_truck_schedule"

    id: Mapped[str]               = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    truck_name: Mapped[str]       = mapped_column(String(200), nullable=False)
    operator_name: Mapped[str]    = mapped_column(String(200), nullable=False)
    cuisine_type: Mapped[str]     = mapped_column(String(100), nullable=False)
    event_date: Mapped[date]      = mapped_column(Date, nullable=False)
    status: Mapped[str]           = mapped_column(SAEnum(FoodTruckStatus), default=FoodTruckStatus.SCHEDULED)
    spot_number: Mapped[int]      = mapped_column(Integer, nullable=False)   # 1–6
    estimated_revenue: Mapped[float]    = mapped_column(Float, default=0.0)
    actual_revenue: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    plaza_fee: Mapped[float]      = mapped_column(Float, default=150.0)  # NXS daily plaza fee
    linked_event_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    notes: Mapped[Optional[str]]  = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime]  = mapped_column(DateTime(timezone=True), server_default=func.now())


class FnBRevenueLedger(Base):
    """Monthly F&B revenue summary ledger."""
    __tablename__ = "fnb_revenue_ledger"

    id: Mapped[str]               = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    month: Mapped[str]            = mapped_column(String(7), nullable=False, unique=True)
    restaurant_revenue: Mapped[float]    = mapped_column(Float, default=0.0)
    concession_revenue: Mapped[float]    = mapped_column(Float, default=0.0)
    food_truck_fees: Mapped[float]       = mapped_column(Float, default=0.0)
    catering_revenue: Mapped[float]      = mapped_column(Float, default=0.0)
    total_revenue: Mapped[float]         = mapped_column(Float, nullable=False)
    total_events: Mapped[int]            = mapped_column(Integer, default=0)
    total_attendees: Mapped[int]         = mapped_column(Integer, default=0)
    avg_per_cap: Mapped[float]           = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime]         = mapped_column(DateTime(timezone=True), server_default=func.now())


# ── Pydantic ──────────────────────────────────────────────────────────────────

class EventCreate(BaseModel):
    venue_id: str
    event_type: EventType
    title: str
    event_date: date
    attendees: int
    per_cap_spend: Optional[float] = None
    food_truck_revenue: float = 0.0
    catering_revenue: float = 0.0
    sponsor_contribution: float = 0.0
    notes: Optional[str] = None


class FoodTruckCreate(BaseModel):
    truck_name: str
    operator_name: str
    cuisine_type: str
    event_date: date
    spot_number: int
    estimated_revenue: float = 0.0
    plaza_fee: float = 150.0
    linked_event_id: Optional[str] = None
    notes: Optional[str] = None


# ── DB dependency ─────────────────────────────────────────────────────────────

async def get_db() -> AsyncSession:
    raise NotImplementedError("Wire to your AsyncSession factory")


# ── Router ────────────────────────────────────────────────────────────────────

router = APIRouter(prefix="/api/fnb", tags=["F&B Restaurant"])
claude = Anthropic()

FNB_CONTEXT = """
You are the AI revenue manager for NXS National Complex Food & Beverage operations, Proctor MN.
Phase 2 restaurant buildout: $720K investment.
Campus venues: Main Restaurant (Phase 2), Concession Stand (Phase 1), Food Truck Plaza (Phase 1, 6 spots),
Catering Kitchen (Phase 2), Bar & Lounge (Phase 2).
Tournament days drive the highest per-cap spend ($18+). League nights average $12/attendee.
Food truck plaza sponsorships: $10K–$50K/year per sponsor.
Revenue is tightly correlated with facility event calendar — tournament, league, and camp activity.
"""


# ── Seed ──────────────────────────────────────────────────────────────────────

@router.post("/seed", summary="Seed F&B venues, events, food trucks, and monthly ledger")
async def seed_fnb(db: AsyncSession = Depends(get_db)) -> dict:
    existing = await db.scalar(select(func.count()).select_from(FnBVenue))
    if existing and existing > 0:
        return {"message": f"Already seeded — {existing} venues exist", "seeded": False}

    today = date.today()
    random.seed(77)

    # ── Venues ────────────────────────────────────────────────────────────────
    venues = [
        FnBVenue(name="NXS Concession Stand",   venue_type=VenueType.CONCESSION_STAND, capacity=0,   is_operational=True,  phase_open=1, buildout_cost=85_000,  description="Phase 1 concession — open during all facility events"),
        FnBVenue(name="NXS Food Truck Plaza",    venue_type=VenueType.FOOD_TRUCK_PLAZA, capacity=200, is_operational=True,  phase_open=1, buildout_cost=45_000,  description="6-spot food truck plaza — adjacent to main entrance"),
        FnBVenue(name="NXS Main Restaurant",     venue_type=VenueType.MAIN_RESTAURANT,  capacity=120, is_operational=False, phase_open=2, buildout_cost=420_000, description="Phase 2 full-service restaurant — 120 seats, full bar, sports viewing"),
        FnBVenue(name="NXS Bar & Lounge",        venue_type=VenueType.BAR_LOUNGE,       capacity=60,  is_operational=False, phase_open=2, buildout_cost=180_000, description="Phase 2 bar and lounge adjacent to main restaurant"),
        FnBVenue(name="NXS Catering Kitchen",    venue_type=VenueType.CATERING_KITCHEN, capacity=0,   is_operational=False, phase_open=2, buildout_cost=75_000,  description="Phase 2 dedicated catering production kitchen"),
    ]
    for v in venues:
        db.add(v)
    await db.flush()

    concession = venues[0]
    food_truck_plaza = venues[1]

    # ── Events — 3 months of history ──────────────────────────────────────────
    event_seeds = []
    for days_ago in range(90, -1, -1):
        edate = today - timedelta(days=days_ago)
        dow = edate.weekday()

        # Tournament days — big revenue
        if random.random() < 0.12:
            att = random.randint(180, 320)
            per_cap = PER_CAP_TARGETS["tournament_day"] + random.uniform(-2, 4)
            gross = round(att * per_cap, 2)
            net = round(gross * 0.68, 2)
            ft_rev = round(random.randint(3, 6) * random.uniform(600, 1200), 2)
            e = FnBEvent(venue_id=concession.id, event_type=EventType.TOURNAMENT,
                title="Tournament Day — NXS", event_date=edate,
                attendees=att, per_cap_spend=round(per_cap, 2),
                gross_revenue=gross, net_revenue=net,
                food_truck_revenue=ft_rev, catering_revenue=round(att * 3.5, 2),
                cogs_pct=0.32)
            event_seeds.append(e)
            db.add(e)

        # League nights — Mon/Wed/Thu/Fri evenings
        elif dow in [0, 2, 3, 4] and random.random() < 0.70:
            att = random.randint(55, 110)
            per_cap = PER_CAP_TARGETS["league_night"] + random.uniform(-2, 3)
            gross = round(att * per_cap, 2)
            net = round(gross * 0.68, 2)
            e = FnBEvent(venue_id=concession.id, event_type=EventType.LEAGUE_NIGHT,
                title="League Night Concessions", event_date=edate,
                attendees=att, per_cap_spend=round(per_cap, 2),
                gross_revenue=gross, net_revenue=net, cogs_pct=0.32)
            event_seeds.append(e)
            db.add(e)

        # Weekend open events
        elif dow >= 5 and random.random() < 0.60:
            att = random.randint(80, 180)
            per_cap = PER_CAP_TARGETS["open_event"] + random.uniform(-1, 3)
            gross = round(att * per_cap, 2)
            net = round(gross * 0.68, 2)
            ft_rev = round(random.randint(2, 4) * random.uniform(400, 900), 2)
            e = FnBEvent(venue_id=concession.id, event_type=EventType.OPEN_EVENT,
                title="Weekend Facility Event", event_date=edate,
                attendees=att, per_cap_spend=round(per_cap, 2),
                gross_revenue=gross, net_revenue=net,
                food_truck_revenue=ft_rev, cogs_pct=0.32)
            event_seeds.append(e)
            db.add(e)

    # ── Upcoming events ────────────────────────────────────────────────────────
    for days_ahead in range(1, 22):
        fdate = today + timedelta(days=days_ahead)
        dow = fdate.weekday()
        if dow in [0, 2, 3, 4]:
            att = random.randint(60, 105)
            e = FnBEvent(venue_id=concession.id, event_type=EventType.LEAGUE_NIGHT,
                title="League Night Concessions", event_date=fdate,
                attendees=att, per_cap_spend=12.0,
                gross_revenue=round(att * 12.0, 2), net_revenue=round(att * 12.0 * 0.68, 2),
                cogs_pct=0.32)
            db.add(e)

    # Tournament upcoming
    tourney_date = today + timedelta(days=14)
    for i in range(3):
        att = random.randint(200, 310)
        e = FnBEvent(venue_id=concession.id, event_type=EventType.TOURNAMENT,
            title="Regional Youth Hockey Tournament", event_date=tourney_date + timedelta(days=i),
            attendees=att, per_cap_spend=18.5,
            gross_revenue=round(att * 18.5, 2), net_revenue=round(att * 18.5 * 0.68, 2),
            food_truck_revenue=round(random.randint(4, 6) * 850.0, 2),
            catering_revenue=round(att * 4.0, 2), cogs_pct=0.32)
        db.add(e)

    # ── Food trucks ────────────────────────────────────────────────────────────
    truck_roster = [
        ("Smoke & Ember BBQ",     "Jake Nilsson",    "BBQ / Comfort"),
        ("Duluth Taco Collective","Maria Rivera",    "Mexican / Fusion"),
        ("North Shore Fish Co.",  "Erik Magnusson",  "Seafood / Walleye"),
        ("Pizza Fire Duluth",     "Angela Torres",   "Wood-fired Pizza"),
        ("Sweet Tooth NMN",       "Priya Patel",     "Desserts / Coffee"),
        ("Loaded Burger Co.",     "Marcus Williams", "Burgers / Fries"),
    ]
    for i, (name, op, cuisine) in enumerate(truck_roster, start=1):
        # 3 upcoming appearances each
        for week in range(3):
            truck_date = today + timedelta(days=(week * 7) + (i % 7))
            truck = FoodTruckSchedule(
                truck_name=name, operator_name=op, cuisine_type=cuisine,
                event_date=truck_date, spot_number=i,
                status=FoodTruckStatus.SCHEDULED,
                estimated_revenue=random.uniform(800, 2200),
                plaza_fee=150.0,
            )
            db.add(truck)

    # ── Monthly ledger ─────────────────────────────────────────────────────────
    for mo_offset in range(3, 0, -1):
        mo_date = today - timedelta(days=30 * mo_offset)
        mo_str  = mo_date.strftime("%Y-%m")
        mo_events = [e for e in event_seeds if e.event_date.strftime("%Y-%m") == mo_str]
        total_rev = sum(e.gross_revenue + e.food_truck_revenue + e.catering_revenue for e in mo_events)
        total_att = sum(e.attendees for e in mo_events)
        ft_fees   = round(len(mo_events) * 0.2 * 150.0, 2)   # approx truck days
        ledger = FnBRevenueLedger(
            month=mo_str,
            restaurant_revenue=0.0,
            concession_revenue=round(sum(e.gross_revenue for e in mo_events), 2),
            food_truck_fees=ft_fees,
            catering_revenue=round(sum(e.catering_revenue for e in mo_events), 2),
            total_revenue=round(total_rev + ft_fees, 2),
            total_events=len(mo_events),
            total_attendees=total_att,
            avg_per_cap=round(total_rev / total_att, 2) if total_att else 0,
        )
        db.add(ledger)

    await db.commit()
    return {
        "message": "F&B module seeded",
        "venues": len(venues),
        "events": len(event_seeds),
        "food_trucks": len(truck_roster) * 3,
        "months_of_history": 3,
        "seeded": True,
    }


# ── Venues ────────────────────────────────────────────────────────────────────

@router.get("/venues", summary="All F&B venues with operational status")
async def list_venues(db: AsyncSession = Depends(get_db)) -> list[dict]:
    result = await db.execute(select(FnBVenue))
    venues = result.scalars().all()
    return [
        {"id": v.id, "name": v.name, "venue_type": v.venue_type,
         "capacity": v.capacity, "is_operational": v.is_operational,
         "phase_open": v.phase_open, "buildout_cost": v.buildout_cost,
         "description": v.description}
        for v in venues
    ]


# ── Events ────────────────────────────────────────────────────────────────────

@router.get("/events", summary="F&B events with revenue")
async def list_events(
    event_type: Optional[EventType] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    q = select(FnBEvent)
    if event_type: q = q.where(FnBEvent.event_type == event_type)
    if from_date:  q = q.where(FnBEvent.event_date >= from_date)
    if to_date:    q = q.where(FnBEvent.event_date <= to_date)
    q = q.order_by(FnBEvent.event_date.desc())
    result = await db.execute(q)
    events = result.scalars().all()
    return [
        {"id": e.id, "venue_id": e.venue_id, "event_type": e.event_type,
         "title": e.title, "event_date": e.event_date.isoformat(),
         "attendees": e.attendees, "per_cap_spend": e.per_cap_spend,
         "gross_revenue": e.gross_revenue, "net_revenue": e.net_revenue,
         "food_truck_revenue": e.food_truck_revenue,
         "catering_revenue": e.catering_revenue,
         "total_event_revenue": round(e.gross_revenue + e.food_truck_revenue + e.catering_revenue + e.sponsor_contribution, 2)}
        for e in events
    ]


@router.post("/events", summary="Log an F&B event")
async def create_event(payload: EventCreate, db: AsyncSession = Depends(get_db)) -> dict:
    per_cap = payload.per_cap_spend or PER_CAP_TARGETS.get(payload.event_type.value, 9.0)
    gross   = round(payload.attendees * per_cap, 2)
    net     = round(gross * 0.68, 2)
    event   = FnBEvent(
        **payload.model_dump(exclude={"per_cap_spend"}),
        per_cap_spend=per_cap, gross_revenue=gross, net_revenue=net, cogs_pct=0.32,
    )
    db.add(event)
    await db.commit()
    return {"id": event.id, "gross_revenue": gross, "net_revenue": net, "message": "Event logged"}


# ── Food Trucks ───────────────────────────────────────────────────────────────

@router.get("/food-truck-schedule", summary="Upcoming food truck schedule")
async def food_truck_schedule(
    days_ahead: int = Query(30),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    today = date.today()
    result = await db.execute(select(FoodTruckSchedule).where(
        FoodTruckSchedule.event_date >= today,
        FoodTruckSchedule.event_date <= today + timedelta(days=days_ahead),
    ).order_by(FoodTruckSchedule.event_date, FoodTruckSchedule.spot_number))
    trucks = result.scalars().all()
    return [
        {"id": t.id, "truck_name": t.truck_name, "operator_name": t.operator_name,
         "cuisine_type": t.cuisine_type, "event_date": t.event_date.isoformat(),
         "spot_number": t.spot_number, "status": t.status,
         "estimated_revenue": t.estimated_revenue, "plaza_fee": t.plaza_fee}
        for t in trucks
    ]


@router.post("/food-trucks", summary="Schedule a food truck appearance")
async def schedule_food_truck(payload: FoodTruckCreate, db: AsyncSession = Depends(get_db)) -> dict:
    if payload.spot_number not in range(1, FOOD_TRUCK_SPOTS + 1):
        raise HTTPException(400, f"Spot number must be 1–{FOOD_TRUCK_SPOTS}")
    truck = FoodTruckSchedule(**payload.model_dump())
    db.add(truck)
    await db.commit()
    return {"message": "Food truck scheduled", "plaza_fee": payload.plaza_fee}


# ── Revenue KPIs ──────────────────────────────────────────────────────────────

@router.get("/revenue-summary", summary="F&B revenue summary — trailing 30/90 days")
async def revenue_summary(db: AsyncSession = Depends(get_db)) -> dict:
    today = date.today()

    async def _stats(start: date, end: date) -> dict:
        q = await db.execute(select(
            func.sum(FnBEvent.gross_revenue),
            func.sum(FnBEvent.net_revenue),
            func.sum(FnBEvent.food_truck_revenue),
            func.sum(FnBEvent.catering_revenue),
            func.count(FnBEvent.id),
            func.sum(FnBEvent.attendees),
        ).where(FnBEvent.event_date.between(start, end)))
        row = q.one()
        gross, net, ft, cat, count, att = (row[i] or 0 for i in range(6))
        return {
            "gross_revenue": round(gross, 2),
            "net_revenue": round(net, 2),
            "food_truck_revenue": round(ft, 2),
            "catering_revenue": round(cat, 2),
            "total_revenue": round(gross + ft + cat, 2),
            "events": count,
            "attendees": att,
            "avg_per_cap": round(gross / att, 2) if att else 0,
        }

    type_q = await db.execute(select(
        FnBEvent.event_type,
        func.sum(FnBEvent.gross_revenue),
        func.count(),
        func.avg(FnBEvent.per_cap_spend),
    ).where(FnBEvent.event_date >= today - timedelta(days=90)).group_by(FnBEvent.event_type))
    type_breakdown = {row[0]: {"revenue": round(row[1] or 0, 2), "events": row[2], "avg_per_cap": round(row[3] or 0, 2)} for row in type_q.all()}

    # Food truck plaza fees MTD
    ft_fees_q = await db.execute(select(func.sum(FoodTruckSchedule.plaza_fee)).where(
        FoodTruckSchedule.event_date >= today.replace(day=1),
        FoodTruckSchedule.status.in_([FoodTruckStatus.ACTIVE, FoodTruckStatus.COMPLETED]),
    ))
    ft_fees_mtd = ft_fees_q.scalar() or 0.0

    ledger_result = await db.execute(select(FnBRevenueLedger).order_by(FnBRevenueLedger.month))
    ledger = ledger_result.scalars().all()

    return {
        "trailing_30": await _stats(today - timedelta(days=30), today),
        "trailing_90": await _stats(today - timedelta(days=90), today),
        "event_type_breakdown": type_breakdown,
        "food_truck_plaza_fees_mtd": round(ft_fees_mtd, 2),
        "per_cap_targets": PER_CAP_TARGETS,
        "phase2_buildout_cost": RESTAURANT_BUILDOUT_COST,
        "monthly_ledger": [{"month": l.month, "total_revenue": l.total_revenue, "events": l.total_events, "attendees": l.total_attendees, "avg_per_cap": l.avg_per_cap} for l in ledger],
    }


# ── AI ────────────────────────────────────────────────────────────────────────

@router.post("/ai-revenue-forecast", summary="AI F&B revenue forecast and optimization")
async def ai_revenue_forecast(db: AsyncSession = Depends(get_db)) -> dict:
    summary = await revenue_summary(db)
    trucks = await food_truck_schedule(db=db)
    venues = await list_venues(db)
    phase2_venues = [v for v in venues if not v["is_operational"]]

    prompt = f"""
NXS F&B Operations — Revenue Forecast & Optimization

CURRENT OPERATIONS (Phase 1 venues operational):
Trailing 30 days:
- Gross revenue: ${summary['trailing_30']['gross_revenue']:,.0f}
- Net revenue: ${summary['trailing_30']['net_revenue']:,.0f}
- Events: {summary['trailing_30']['events']} | Attendees: {summary['trailing_30']['attendees']:,}
- Avg per cap: ${summary['trailing_30']['avg_per_cap']} (targets: tournament ${PER_CAP_TARGETS['tournament_day']}, league ${PER_CAP_TARGETS['league_night']})
- Food truck revenue: ${summary['trailing_30']['food_truck_revenue']:,.0f}
- Catering revenue: ${summary['trailing_30']['catering_revenue']:,.0f}

EVENT MIX PERFORMANCE:
{chr(10).join(f"  {k}: ${v['revenue']:,.0f} rev | {v['events']} events | ${v['avg_per_cap']} avg/person" for k, v in summary['event_type_breakdown'].items())}

UPCOMING FOOD TRUCKS: {len(trucks)} scheduled in next 30 days

PHASE 2 VENUES PENDING (${RESTAURANT_BUILDOUT_COST:,.0f} buildout):
{chr(10).join(f"  {v['name']} ({v['venue_type']}) — Cap: {v['capacity']} — Cost: ${v['buildout_cost']:,.0f}" for v in phase2_venues)}

Per-cap targets: Tournament ${PER_CAP_TARGETS['tournament_day']} | League ${PER_CAP_TARGETS['league_night']} | Open ${PER_CAP_TARGETS['open_event']}

Generate a 3-paragraph forecast:
1. Current revenue performance — are per-cap targets being hit? Which event types are over/under-performing and why?
2. Tournament correlation strategy — the biggest revenue lever. How to maximize F&B revenue on tournament days (pre-orders, package deals, food truck activation, catering bundles)?
3. Phase 2 revenue projection — once the main restaurant + bar open, what's the realistic annual F&B revenue target? What's the payback period on the $720K buildout at projected volumes?
"""

    response = claude.messages.create(
        model="claude-opus-4-5",
        max_tokens=700,
        system=FNB_CONTEXT,
        messages=[{"role": "user", "content": prompt}],
    )

    return {
        "forecast": response.content[0].text,
        "summary": summary,
        "generated_at": datetime.utcnow().isoformat(),
    }


@router.post("/ai-event-day-plan", summary="AI event-day F&B activation plan")
async def ai_event_day_plan(
    event_type: EventType = Query(EventType.TOURNAMENT),
    expected_attendees: int = Query(250),
    db: AsyncSession = Depends(get_db),
) -> dict:
    target_per_cap = PER_CAP_TARGETS.get(event_type.value, 9.0)
    target_rev = round(expected_attendees * target_per_cap, 2)
    trucks_available = FOOD_TRUCK_SPOTS

    prompt = f"""
NXS F&B — Event Day Activation Plan

Event type: {event_type.value.replace("_", " ").title()}
Expected attendees: {expected_attendees:,}
Target per-cap spend: ${target_per_cap}
Target gross revenue: ${target_rev:,.0f}
Food truck spots available: {trucks_available}

Create a specific event-day F&B activation plan:
1. Staffing and station setup (concession stand + food trucks + catering)
2. Menu and pricing recommendations to hit ${target_per_cap}/person
3. Pre-event marketing push (what to send 48hrs before to drive pre-orders and food truck awareness)
Keep it to 3 concise, actionable paragraphs.
"""

    response = claude.messages.create(
        model="claude-opus-4-5",
        max_tokens=500,
        system=FNB_CONTEXT,
        messages=[{"role": "user", "content": prompt}],
    )

    return {
        "plan": response.content[0].text,
        "event_type": event_type,
        "expected_attendees": expected_attendees,
        "target_revenue": target_rev,
        "generated_at": datetime.utcnow().isoformat(),
    }
