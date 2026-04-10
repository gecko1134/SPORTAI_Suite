"""
SportAI Suite — Ice Rink Module
Sprint 5 · NXS National Complex
200×85 ft NHL-spec rink · Ice vs. turf conversion scheduling
Hockey, figure skating, open skate, leagues · Prime time optimization
Cross-pricing with dome turf

Add to main.py:
    from routers.rink_ai import router as rink_router
    app.include_router(rink_router)
"""

from __future__ import annotations

import enum
import uuid
from datetime import date, datetime, time, timedelta
from typing import Optional
import random

from anthropic import Anthropic
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import (
    Boolean, Date, DateTime, Enum as SAEnum,
    Float, Integer, String, Text, Time, func, select
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# ── Constants ─────────────────────────────────────────────────────────────────

RINK_DIMENSIONS   = "200ft × 85ft (NHL specification)"
RINK_CAPACITY     = 500           # spectators
ICE_MAKE_HOURS    = 8             # hours to make ice from turf
ICE_REMOVE_HOURS  = 6             # hours to remove ice back to turf
ICE_MAKE_COST     = 1_200.0       # $ cost to convert from turf → ice
ICE_REMOVE_COST   = 800.0         # $ cost to convert from ice → turf

BASE_RATES = {
    "hockey_prime":   280.0,   # $/hr prime (5–10pm, weekends)
    "hockey_off":     180.0,   # $/hr off-peak
    "figure_skating": 200.0,   # $/hr
    "open_skate":      8.0,    # $/person
    "learn_to_skate": 12.0,    # $/person
    "league_block":   220.0,   # $/hr (negotiated)
    "tournament":     320.0,   # $/hr tournament rate
    "turf_prime":     200.0,   # $/hr when converted to turf
    "turf_off":       120.0,   # $/hr turf off-peak
}


# ── Enums ─────────────────────────────────────────────────────────────────────

class SurfaceType(str, enum.Enum):
    ICE  = "ice"
    TURF = "turf"


class SessionCategory(str, enum.Enum):
    HOCKEY_PRIME    = "hockey_prime"
    HOCKEY_OFF      = "hockey_off"
    FIGURE_SKATING  = "figure_skating"
    OPEN_SKATE      = "open_skate"
    LEARN_TO_SKATE  = "learn_to_skate"
    LEAGUE_BLOCK    = "league_block"
    TOURNAMENT      = "tournament"
    TURF_PRIME      = "turf_prime"
    TURF_OFF        = "turf_off"
    MAINTENANCE     = "maintenance"
    DARK            = "dark"          # unbooked


class BookingStatus(str, enum.Enum):
    CONFIRMED  = "confirmed"
    TENTATIVE  = "tentative"
    COMPLETED  = "completed"
    CANCELLED  = "cancelled"


class ConversionDirection(str, enum.Enum):
    TURF_TO_ICE = "turf_to_ice"
    ICE_TO_TURF = "ice_to_turf"


# ── ORM Models ────────────────────────────────────────────────────────────────

class RinkSession(Base):
    """Scheduled rink session — ice or turf use."""
    __tablename__ = "rink_sessions"

    id: Mapped[str]               = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    surface: Mapped[str]          = mapped_column(SAEnum(SurfaceType), nullable=False)
    category: Mapped[str]         = mapped_column(SAEnum(SessionCategory), nullable=False)
    title: Mapped[str]            = mapped_column(String(200), nullable=False)
    session_date: Mapped[date]    = mapped_column(Date, nullable=False)
    start_time: Mapped[time]      = mapped_column(Time, nullable=False)
    end_time: Mapped[time]        = mapped_column(Time, nullable=False)
    duration_hours: Mapped[float] = mapped_column(Float, nullable=False)
    rate_per_hour: Mapped[float]  = mapped_column(Float, nullable=False)
    attendees: Mapped[Optional[int]]    = mapped_column(Integer, nullable=True)
    revenue: Mapped[float]              = mapped_column(Float, nullable=False)
    status: Mapped[str]                 = mapped_column(SAEnum(BookingStatus), default=BookingStatus.CONFIRMED)
    group_name: Mapped[Optional[str]]   = mapped_column(String(200), nullable=True)
    contact_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    notes: Mapped[Optional[str]]        = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime]        = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime]        = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class RinkLeagueBlock(Base):
    """Recurring league block — weekly guaranteed ice/turf time."""
    __tablename__ = "rink_league_blocks"

    id: Mapped[str]             = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    league_name: Mapped[str]    = mapped_column(String(200), nullable=False)
    sport: Mapped[str]          = mapped_column(String(100), nullable=False)  # hockey, figure_skating, etc
    surface: Mapped[str]        = mapped_column(SAEnum(SurfaceType), nullable=False)
    day_of_week: Mapped[int]    = mapped_column(Integer, nullable=False)   # 0=Mon…6=Sun
    start_time: Mapped[time]    = mapped_column(Time, nullable=False)
    end_time: Mapped[time]      = mapped_column(Time, nullable=False)
    duration_hours: Mapped[float] = mapped_column(Float, nullable=False)
    teams: Mapped[int]          = mapped_column(Integer, nullable=False)
    players_per_team: Mapped[int]= mapped_column(Integer, default=15)
    weekly_rate: Mapped[float]  = mapped_column(Float, nullable=False)
    season_start: Mapped[date]  = mapped_column(Date, nullable=False)
    season_end: Mapped[date]    = mapped_column(Date, nullable=False)
    is_active: Mapped[bool]     = mapped_column(Boolean, default=True)
    contact_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    notes: Mapped[Optional[str]]        = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime]        = mapped_column(DateTime(timezone=True), server_default=func.now())

    @property
    def annual_value(self) -> float:
        weeks = max(1, (self.season_end - self.season_start).days // 7)
        return round(self.weekly_rate * weeks, 2)

    @property
    def total_participants(self) -> int:
        return self.teams * self.players_per_team


class RinkConversionLog(Base):
    """Log of ice ↔ turf conversion events."""
    __tablename__ = "rink_conversion_log"

    id: Mapped[str]                = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    direction: Mapped[str]         = mapped_column(SAEnum(ConversionDirection), nullable=False)
    conversion_date: Mapped[date]  = mapped_column(Date, nullable=False)
    reason: Mapped[Optional[str]]  = mapped_column(String(300), nullable=True)
    cost: Mapped[float]            = mapped_column(Float, nullable=False)
    duration_hours: Mapped[float]  = mapped_column(Float, nullable=False)
    completed: Mapped[bool]        = mapped_column(Boolean, default=True)
    notes: Mapped[Optional[str]]   = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime]   = mapped_column(DateTime(timezone=True), server_default=func.now())


# ── Pydantic ──────────────────────────────────────────────────────────────────

class SessionCreate(BaseModel):
    surface: SurfaceType
    category: SessionCategory
    title: str
    session_date: date
    start_time: time
    end_time: time
    rate_per_hour: Optional[float] = None
    attendees: Optional[int] = None
    group_name: Optional[str] = None
    contact_name: Optional[str] = None
    notes: Optional[str] = None


class LeagueBlockCreate(BaseModel):
    league_name: str
    sport: str
    surface: SurfaceType
    day_of_week: int
    start_time: time
    end_time: time
    teams: int
    players_per_team: int = 15
    weekly_rate: float
    season_start: date
    season_end: date
    contact_name: Optional[str] = None
    notes: Optional[str] = None


# ── DB dependency ─────────────────────────────────────────────────────────────

async def get_db() -> AsyncSession:
    raise NotImplementedError("Replace with: from database import get_db  # then remove this function")


# ── Router ────────────────────────────────────────────────────────────────────

router = APIRouter(prefix="/api/rink", tags=["Ice Rink"])
claude = Anthropic()

RINK_CONTEXT = """
You are the AI revenue manager for the NXS National Complex Ice Rink — 200×85 ft NHL-spec rink,
704 Kirkus Street, Proctor MN 55810. The rink can convert between ice and turf surfaces.
Ice conversion costs $1,200 (turf→ice, 8hr) and $800 (ice→turf, 6hr).
Revenue targets: maximize prime-time utilization, reduce dark ice, balance ice vs turf scheduling.
Hockey leagues, figure skating, open skate, tournaments, and turf events all compete for the surface.
Provide specific, revenue-focused scheduling and optimization insights.
"""

DAY_NAMES = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]


# ── Seed ──────────────────────────────────────────────────────────────────────

@router.post("/seed", summary="Seed rink sessions, league blocks, and conversion history")
async def seed_rink(db: AsyncSession = Depends(get_db)) -> dict:
    existing = await db.scalar(select(func.count()).select_from(RinkSession))
    if existing and existing > 0:
        return {"message": f"Already seeded — {existing} sessions exist", "seeded": False}

    today = date.today()
    random.seed(99)

    # ── League blocks ─────────────────────────────────────────────────────────
    season_start = today - timedelta(days=60)
    season_end   = today + timedelta(days=120)

    leagues = [
        LeagueBlockCreate(league_name="NXS Adult Hockey League — Monday",   sport="ice_hockey", surface=SurfaceType.ICE,  day_of_week=0, start_time=time(20,0), end_time=time(22,0), teams=6, players_per_team=16, weekly_rate=440.0, season_start=season_start, season_end=season_end),
        LeagueBlockCreate(league_name="NXS Adult Hockey League — Wednesday", sport="ice_hockey", surface=SurfaceType.ICE,  day_of_week=2, start_time=time(20,0), end_time=time(22,0), teams=6, players_per_team=16, weekly_rate=440.0, season_start=season_start, season_end=season_end),
        LeagueBlockCreate(league_name="Figure Skating Club — Tuesday AM",    sport="figure_skating", surface=SurfaceType.ICE, day_of_week=1, start_time=time(6,0), end_time=time(9,0), teams=1, players_per_team=18, weekly_rate=600.0, season_start=season_start, season_end=season_end),
        LeagueBlockCreate(league_name="Figure Skating Club — Thursday AM",   sport="figure_skating", surface=SurfaceType.ICE, day_of_week=3, start_time=time(6,0), end_time=time(9,0), teams=1, players_per_team=18, weekly_rate=600.0, season_start=season_start, season_end=season_end),
        LeagueBlockCreate(league_name="Youth Hockey Development",            sport="ice_hockey", surface=SurfaceType.ICE,  day_of_week=6, start_time=time(8,0), end_time=time(12,0), teams=4, players_per_team=14, weekly_rate=880.0, season_start=season_start, season_end=season_end),
        LeagueBlockCreate(league_name="Open Skate — Friday Eve",             sport="open_skate", surface=SurfaceType.ICE,  day_of_week=4, start_time=time(18,0), end_time=time(20,0), teams=1, players_per_team=80, weekly_rate=640.0, season_start=season_start, season_end=season_end),
    ]
    created_leagues = []
    for l_data in leagues:
        dur = (datetime.combine(date.today(), l_data.end_time) - datetime.combine(date.today(), l_data.start_time)).seconds / 3600
        lb = RinkLeagueBlock(**l_data.model_dump(), duration_hours=dur)
        db.add(lb)
        created_leagues.append(lb)

    # ── Sessions — 6 weeks of history + 3 weeks future ────────────────────────
    sessions_created = 0
    for day_offset in range(-42, 22):
        sdate = today + timedelta(days=day_offset)
        dow = sdate.weekday()
        is_weekend = dow >= 5
        is_past = sdate < today

        # Morning figure skating
        if dow in [1, 3]:
            rev = BASE_RATES["figure_skating"] * 3
            s = RinkSession(surface=SurfaceType.ICE, category=SessionCategory.FIGURE_SKATING,
                title="NXS Figure Skating Club", session_date=sdate,
                start_time=time(6,0), end_time=time(9,0), duration_hours=3.0,
                rate_per_hour=BASE_RATES["figure_skating"], revenue=rev,
                attendees=18, group_name="NXS Figure Skating Club",
                status=BookingStatus.COMPLETED if is_past else BookingStatus.CONFIRMED)
            db.add(s); sessions_created += 1

        # Learn-to-skate — Saturday morning
        if dow == 5:
            att = random.randint(22, 35)
            rev = att * BASE_RATES["learn_to_skate"]
            s = RinkSession(surface=SurfaceType.ICE, category=SessionCategory.LEARN_TO_SKATE,
                title="Learn to Skate Program", session_date=sdate,
                start_time=time(9,0), end_time=time(10,30), duration_hours=1.5,
                rate_per_hour=0, revenue=rev, attendees=att,
                status=BookingStatus.COMPLETED if is_past else BookingStatus.CONFIRMED)
            db.add(s); sessions_created += 1

        # Open skate — Friday evening
        if dow == 4:
            att = random.randint(55, 90)
            rev = att * BASE_RATES["open_skate"]
            s = RinkSession(surface=SurfaceType.ICE, category=SessionCategory.OPEN_SKATE,
                title="Public Open Skate", session_date=sdate,
                start_time=time(18,0), end_time=time(20,0), duration_hours=2.0,
                rate_per_hour=0, revenue=rev, attendees=att,
                status=BookingStatus.COMPLETED if is_past else BookingStatus.CONFIRMED)
            db.add(s); sessions_created += 1

        # Adult hockey leagues — Mon, Wed evenings
        if dow in [0, 2]:
            rev = BASE_RATES["league_block"] * 2
            s = RinkSession(surface=SurfaceType.ICE, category=SessionCategory.LEAGUE_BLOCK,
                title=f"Adult Hockey League — {DAY_NAMES[dow]}", session_date=sdate,
                start_time=time(20,0), end_time=time(22,0), duration_hours=2.0,
                rate_per_hour=BASE_RATES["league_block"], revenue=rev,
                attendees=random.randint(22, 30), group_name="NXS Adult Hockey League",
                status=BookingStatus.COMPLETED if is_past else BookingStatus.CONFIRMED)
            db.add(s); sessions_created += 1

        # Youth hockey — Sunday AM
        if dow == 6:
            rev = BASE_RATES["hockey_prime"] * 4
            s = RinkSession(surface=SurfaceType.ICE, category=SessionCategory.HOCKEY_PRIME,
                title="Youth Hockey Development", session_date=sdate,
                start_time=time(8,0), end_time=time(12,0), duration_hours=4.0,
                rate_per_hour=BASE_RATES["hockey_prime"], revenue=rev,
                attendees=random.randint(40, 56), group_name="NXS Youth Hockey",
                status=BookingStatus.COMPLETED if is_past else BookingStatus.CONFIRMED)
            db.add(s); sessions_created += 1

        # Occasional prime hockey rentals
        if random.random() < 0.4 and is_weekend:
            rev = BASE_RATES["hockey_prime"] * 1.5
            s = RinkSession(surface=SurfaceType.ICE, category=SessionCategory.HOCKEY_PRIME,
                title="Prime Ice Rental", session_date=sdate,
                start_time=time(17,0), end_time=time(18,30), duration_hours=1.5,
                rate_per_hour=BASE_RATES["hockey_prime"], revenue=rev,
                attendees=random.randint(14, 22),
                status=BookingStatus.COMPLETED if is_past else BookingStatus.CONFIRMED)
            db.add(s); sessions_created += 1

        # Turf conversion sessions — occasional weekday afternoons
        if random.random() < 0.15 and not is_weekend and day_offset > -14:
            rev = BASE_RATES["turf_prime"] * 2
            s = RinkSession(surface=SurfaceType.TURF, category=SessionCategory.TURF_PRIME,
                title="Turf Rental — Afternoon Block", session_date=sdate,
                start_time=time(13,0), end_time=time(15,0), duration_hours=2.0,
                rate_per_hour=BASE_RATES["turf_prime"], revenue=rev,
                status=BookingStatus.CONFIRMED if not is_past else BookingStatus.COMPLETED)
            db.add(s); sessions_created += 1

    # ── Upcoming tournament ───────────────────────────────────────────────────
    tourney_date = today + timedelta(days=14)
    for i in range(3):
        rev = BASE_RATES["tournament"] * 3
        s = RinkSession(surface=SurfaceType.ICE, category=SessionCategory.TOURNAMENT,
            title="Regional Youth Hockey Tournament", session_date=tourney_date + timedelta(days=i),
            start_time=time(8,0), end_time=time(18,0), duration_hours=10.0,
            rate_per_hour=BASE_RATES["tournament"], revenue=rev * (10/3),
            attendees=random.randint(150, 280), group_name="MN Youth Hockey Assoc",
            status=BookingStatus.CONFIRMED)
        db.add(s); sessions_created += 1

    # ── Conversion log ────────────────────────────────────────────────────────
    conversions = [
        RinkConversionLog(direction=ConversionDirection.TURF_TO_ICE, conversion_date=today - timedelta(days=90), reason="Hockey season start", cost=ICE_MAKE_COST, duration_hours=ICE_MAKE_HOURS),
        RinkConversionLog(direction=ConversionDirection.ICE_TO_TURF, conversion_date=today - timedelta(days=45), reason="Indoor soccer tournament", cost=ICE_REMOVE_COST, duration_hours=ICE_REMOVE_HOURS),
        RinkConversionLog(direction=ConversionDirection.TURF_TO_ICE, conversion_date=today - timedelta(days=42), reason="Return to hockey schedule", cost=ICE_MAKE_COST, duration_hours=ICE_MAKE_HOURS),
        RinkConversionLog(direction=ConversionDirection.ICE_TO_TURF, conversion_date=today + timedelta(days=60), reason="Summer lacrosse season", cost=ICE_REMOVE_COST, duration_hours=ICE_REMOVE_HOURS, completed=False),
    ]
    for c in conversions:
        db.add(c)

    await db.commit()
    return {
        "message": "Ice Rink module seeded",
        "sessions": sessions_created + 3,
        "league_blocks": len(leagues),
        "conversions": len(conversions),
        "seeded": True,
    }


# ── Schedule ──────────────────────────────────────────────────────────────────

@router.get("/schedule", summary="Rink schedule — date range with all sessions")
async def rink_schedule(
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    surface: Optional[SurfaceType] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    today = date.today()
    fd = from_date or today
    td = to_date or today + timedelta(days=14)
    q = select(RinkSession).where(
        RinkSession.session_date >= fd,
        RinkSession.session_date <= td,
    )
    if surface:
        q = q.where(RinkSession.surface == surface)
    q = q.order_by(RinkSession.session_date, RinkSession.start_time)
    result = await db.execute(q)
    sessions = result.scalars().all()
    return [
        {"id": s.id, "surface": s.surface, "category": s.category, "title": s.title,
         "session_date": s.session_date.isoformat(),
         "start_time": s.start_time.strftime("%H:%M"),
         "end_time": s.end_time.strftime("%H:%M"),
         "duration_hours": s.duration_hours, "rate_per_hour": s.rate_per_hour,
         "attendees": s.attendees, "revenue": s.revenue,
         "status": s.status, "group_name": s.group_name}
        for s in sessions
    ]


@router.post("/sessions", summary="Book a new rink session")
async def create_session(payload: SessionCreate, db: AsyncSession = Depends(get_db)) -> dict:
    start_dt = datetime.combine(date.today(), payload.start_time)
    end_dt   = datetime.combine(date.today(), payload.end_time)
    hours    = (end_dt - start_dt).seconds / 3600
    rate     = payload.rate_per_hour or BASE_RATES.get(payload.category.value, 200.0)
    revenue  = round(rate * hours, 2)
    session  = RinkSession(
        **payload.model_dump(exclude={"rate_per_hour"}),
        duration_hours=hours, rate_per_hour=rate, revenue=revenue,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return {"id": session.id, "revenue": revenue, "message": "Session booked"}


# ── Leagues ───────────────────────────────────────────────────────────────────

@router.get("/leagues", summary="All league blocks with season value")
async def list_leagues(db: AsyncSession = Depends(get_db)) -> list[dict]:
    result = await db.execute(select(RinkLeagueBlock).where(RinkLeagueBlock.is_active == True))
    leagues = result.scalars().all()
    return [
        {"id": l.id, "league_name": l.league_name, "sport": l.sport, "surface": l.surface,
         "day_of_week": DAY_NAMES[l.day_of_week], "start_time": l.start_time.strftime("%H:%M"),
         "end_time": l.end_time.strftime("%H:%M"), "duration_hours": l.duration_hours,
         "teams": l.teams, "total_participants": l.total_participants,
         "weekly_rate": l.weekly_rate, "annual_value": l.annual_value,
         "season_start": l.season_start.isoformat(), "season_end": l.season_end.isoformat(),
         "contact_name": l.contact_name}
        for l in leagues
    ]


# ── Revenue & Utilization ─────────────────────────────────────────────────────

@router.get("/utilization", summary="Ice utilization and revenue — trailing 30/90 days")
async def utilization(db: AsyncSession = Depends(get_db)) -> dict:
    today = date.today()

    async def _stats(start: date, end: date) -> dict:
        q = await db.execute(select(
            func.sum(RinkSession.revenue),
            func.sum(RinkSession.duration_hours),
            func.count(RinkSession.id),
            func.sum(RinkSession.attendees),
        ).where(
            RinkSession.session_date >= start,
            RinkSession.session_date <= end,
            RinkSession.status.in_([BookingStatus.CONFIRMED, BookingStatus.COMPLETED]),
            RinkSession.category != SessionCategory.DARK,
        ))
        row = q.one()
        revenue, hours, count, att = row[0] or 0, row[1] or 0, row[2] or 0, row[3] or 0
        days_in_range = (end - start).days + 1
        available_hours = days_in_range * 16  # 6am–10pm
        return {
            "revenue": round(revenue, 2),
            "hours_booked": round(hours, 1),
            "available_hours": available_hours,
            "utilization_pct": round(hours / available_hours * 100, 1) if available_hours else 0,
            "sessions": count,
            "total_attendees": att or 0,
            "avg_revenue_per_hour": round(revenue / hours, 2) if hours else 0,
        }

    surface_q = await db.execute(select(
        RinkSession.surface, func.sum(RinkSession.revenue), func.sum(RinkSession.duration_hours)
    ).where(
        RinkSession.session_date >= today - timedelta(days=30),
        RinkSession.status.in_([BookingStatus.CONFIRMED, BookingStatus.COMPLETED]),
    ).group_by(RinkSession.surface))
    surface_split = {row[0]: {"revenue": round(row[1] or 0, 2), "hours": round(row[2] or 0, 1)} for row in surface_q.all()}

    category_q = await db.execute(select(
        RinkSession.category, func.sum(RinkSession.revenue), func.count()
    ).where(
        RinkSession.session_date >= today - timedelta(days=30),
        RinkSession.status.in_([BookingStatus.CONFIRMED, BookingStatus.COMPLETED]),
    ).group_by(RinkSession.category))
    category_breakdown = {row[0]: {"revenue": round(row[1] or 0, 2), "sessions": row[2]} for row in category_q.all()}

    conversions_q = await db.execute(select(func.count(), func.sum(RinkConversionLog.cost)).select_from(RinkConversionLog))
    conv_row = conversions_q.one()
    leagues = await list_leagues(db)
    annual_league_value = sum(l["annual_value"] for l in leagues)

    return {
        "trailing_30": await _stats(today - timedelta(days=30), today),
        "trailing_90": await _stats(today - timedelta(days=90), today),
        "surface_split_30d": surface_split,
        "category_breakdown_30d": category_breakdown,
        "conversion_stats": {"total_conversions": conv_row[0], "total_cost": round(conv_row[1] or 0, 2)},
        "league_annual_value": round(annual_league_value, 2),
        "dimensions": RINK_DIMENSIONS,
        "capacity": RINK_CAPACITY,
    }


@router.get("/conversion-log", summary="Ice ↔ turf conversion history")
async def conversion_log(db: AsyncSession = Depends(get_db)) -> list[dict]:
    result = await db.execute(select(RinkConversionLog).order_by(RinkConversionLog.conversion_date))
    logs = result.scalars().all()
    return [
        {"id": l.id, "direction": l.direction, "conversion_date": l.conversion_date.isoformat(),
         "reason": l.reason, "cost": l.cost, "duration_hours": l.duration_hours,
         "completed": l.completed, "notes": l.notes}
        for l in logs
    ]


# ── AI ────────────────────────────────────────────────────────────────────────

@router.post("/ai-optimizer", summary="AI scheduling and revenue optimization for the rink")
async def ai_optimizer(db: AsyncSession = Depends(get_db)) -> dict:
    util = await utilization(db)
    leagues = await list_leagues(db)
    upcoming = await rink_schedule(db=db)

    prompt = f"""
NXS Ice Rink — Revenue Optimization Brief
{RINK_DIMENSIONS} · Capacity: {RINK_CAPACITY} spectators
Conversion costs: Turf→Ice ${ICE_MAKE_COST:,.0f} ({ICE_MAKE_HOURS}hr) | Ice→Turf ${ICE_REMOVE_COST:,.0f} ({ICE_REMOVE_HOURS}hr)

TRAILING 30 DAYS:
- Revenue: ${util['trailing_30']['revenue']:,.0f}
- Hours booked: {util['trailing_30']['hours_booked']} / {util['trailing_30']['available_hours']} available ({util['trailing_30']['utilization_pct']}%)
- Sessions: {util['trailing_30']['sessions']} | Avg $/hr: ${util['trailing_30']['avg_revenue_per_hour']}
- Attendees: {util['trailing_30']['total_attendees']:,}

SURFACE SPLIT (30d): {util['surface_split_30d']}
TOP REVENUE CATEGORIES: {dict(sorted(util['category_breakdown_30d'].items(), key=lambda x: x[1]['revenue'], reverse=True)[:4])}

LEAGUE PORTFOLIO ({len(leagues)} blocks):
{chr(10).join(f"  {l['league_name']}: {l['day_of_week']} {l['start_time']}–{l['end_time']}, {l['teams']} teams, ${l['weekly_rate']}/wk (${l['annual_value']:,.0f}/season)" for l in leagues)}
Annual league value: ${util['league_annual_value']:,.0f}

UPCOMING 14 DAYS: {len(upcoming)} sessions scheduled

BASE RATES: Hockey prime ${BASE_RATES['hockey_prime']}/hr | Tournament ${BASE_RATES['tournament']}/hr | Open skate ${BASE_RATES['open_skate']}/person

Generate a 3-paragraph revenue optimization brief:
1. Utilization analysis — which hours/days are dark ice and generating zero revenue, and what's the dollar opportunity?
2. Surface conversion strategy — when is it worth converting to turf vs. keeping ice, given conversion costs and potential turf revenue?
3. Revenue growth actions — 3 specific programs to add (early morning open skate, corporate hockey nights, tournament marketing push) with projected revenue impact per program
"""

    response = claude.messages.create(
        model="claude-opus-4-5",
        max_tokens=700,
        system=RINK_CONTEXT,
        messages=[{"role": "user", "content": prompt}],
    )

    return {
        "optimization": response.content[0].text,
        "utilization": util,
        "generated_at": datetime.utcnow().isoformat(),
    }


@router.post("/ai-conversion-recommendation", summary="AI recommendation: keep ice or convert to turf?")
async def ai_conversion_recommendation(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: AsyncSession = Depends(get_db),
) -> dict:
    days = (end_date - start_date).days + 1
    ice_sessions = await rink_schedule(from_date=start_date, to_date=end_date, surface=SurfaceType.ICE, db=db)
    turf_sessions = await rink_schedule(from_date=start_date, to_date=end_date, surface=SurfaceType.TURF, db=db)

    ice_rev  = sum(s["revenue"] for s in ice_sessions)
    turf_rev = sum(s["revenue"] for s in turf_sessions)
    net_if_convert = turf_rev - ICE_REMOVE_COST - ICE_MAKE_COST
    keep_ice_advantage = ice_rev - net_if_convert

    prompt = f"""
NXS Rink — Conversion Decision: {start_date} to {end_date} ({days} days)

OPTION A — Keep Ice:
- Booked ice revenue: ${ice_rev:,.0f}
- Conversion cost: $0
- Net: ${ice_rev:,.0f}

OPTION B — Convert to Turf then Back:
- Booked turf revenue: ${turf_rev:,.0f}
- Conversion cost (out + back): ${ICE_REMOVE_COST + ICE_MAKE_COST:,.0f}
- Net: ${net_if_convert:,.0f}

Keep ice advantage: ${keep_ice_advantage:,.0f}

In 2 paragraphs: (1) Recommend whether to convert or stay ice, with specific reasoning.
(2) What additional bookings would make the conversion worthwhile — what revenue threshold justifies the ${ICE_REMOVE_COST + ICE_MAKE_COST:,.0f} cost?
"""

    response = claude.messages.create(
        model="claude-opus-4-5",
        max_tokens=400,
        system=RINK_CONTEXT,
        messages=[{"role": "user", "content": prompt}],
    )

    return {
        "recommendation": response.content[0].text,
        "ice_revenue_booked": round(ice_rev, 2),
        "turf_revenue_booked": round(turf_rev, 2),
        "conversion_cost_roundtrip": ICE_REMOVE_COST + ICE_MAKE_COST,
        "net_if_convert": round(net_if_convert, 2),
        "keep_ice_advantage": round(keep_ice_advantage, 2),
        "verdict": "KEEP ICE" if keep_ice_advantage > 0 else "CONVERT TO TURF",
    }
