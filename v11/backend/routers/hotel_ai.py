"""
SportAI Suite — Hotel Revenue Module
Sprint 3 · NXS National Complex
85-unit property · Occupancy · ADR · RevPAR · TID Assessment · Dynamic Rate Management
Tournament-correlated demand · AI rate recommendations

Add to main.py:
    from routers.hotel_ai import router as hotel_router
    app.include_router(hotel_router)
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
    Float, ForeignKey, Integer, String, Text, func, select, and_
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# ── Enums ─────────────────────────────────────────────────────────────────────

class RoomType(str, enum.Enum):
    STANDARD_KING   = "standard_king"
    STANDARD_DOUBLE = "standard_double"
    SUITE_KING      = "suite_king"
    ACCESSIBLE      = "accessible"
    TOURNAMENT_BLOCK = "tournament_block"   # bulk group rate


class RoomStatus(str, enum.Enum):
    AVAILABLE   = "available"
    OCCUPIED    = "occupied"
    MAINTENANCE = "maintenance"
    BLOCKED     = "blocked"


class BookingStatus(str, enum.Enum):
    CONFIRMED  = "confirmed"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"
    CANCELLED  = "cancelled"
    NO_SHOW    = "no_show"


class RateStrategy(str, enum.Enum):
    STANDARD   = "standard"
    TOURNAMENT = "tournament"    # +25–40% during events
    PEAK       = "peak"          # holidays, high-demand
    RESCUE     = "rescue"        # <40% occupancy — discount
    GROUP      = "group"         # negotiated block


# ── Base rates ─────────────────────────────────────────────────────────────────

BASE_RATES = {
    RoomType.STANDARD_KING:    109.0,
    RoomType.STANDARD_DOUBLE:  99.0,
    RoomType.SUITE_KING:       159.0,
    RoomType.ACCESSIBLE:       109.0,
    RoomType.TOURNAMENT_BLOCK: 89.0,
}

STRATEGY_MULTIPLIERS = {
    RateStrategy.STANDARD:   1.0,
    RateStrategy.TOURNAMENT: 1.35,
    RateStrategy.PEAK:       1.25,
    RateStrategy.RESCUE:     0.80,
    RateStrategy.GROUP:      0.85,
}

TOTAL_ROOMS = 85
TID_RATE    = 0.015   # 1.5% Tourism Improvement District assessment on room revenue


# ── ORM Models ────────────────────────────────────────────────────────────────

class HotelRoom(Base):
    """Individual hotel room in the 85-unit NXS property."""
    __tablename__ = "hotel_rooms"

    id: Mapped[str]              = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    room_number: Mapped[str]     = mapped_column(String(10), nullable=False, unique=True)
    room_type: Mapped[str]       = mapped_column(SAEnum(RoomType), nullable=False)
    floor: Mapped[int]           = mapped_column(Integer, nullable=False)
    status: Mapped[str]          = mapped_column(SAEnum(RoomStatus), default=RoomStatus.AVAILABLE)
    base_rate: Mapped[float]     = mapped_column(Float, nullable=False)
    max_occupancy: Mapped[int]   = mapped_column(Integer, default=2)
    amenities: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool]      = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    reservations: Mapped[list["HotelReservation"]] = relationship("HotelReservation", back_populates="room", cascade="all, delete-orphan")


class HotelReservation(Base):
    """Hotel reservation — tracks guest stay, rate, and revenue."""
    __tablename__ = "hotel_reservations"

    id: Mapped[str]               = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    room_id: Mapped[str]          = mapped_column(ForeignKey("hotel_rooms.id"), nullable=False)
    guest_name: Mapped[str]       = mapped_column(String(200), nullable=False)
    guest_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    guest_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    check_in: Mapped[date]        = mapped_column(Date, nullable=False)
    check_out: Mapped[date]       = mapped_column(Date, nullable=False)
    nights: Mapped[int]           = mapped_column(Integer, nullable=False)
    guests: Mapped[int]           = mapped_column(Integer, default=1)
    rate_per_night: Mapped[float] = mapped_column(Float, nullable=False)
    total_revenue: Mapped[float]  = mapped_column(Float, nullable=False)
    rate_strategy: Mapped[str]    = mapped_column(SAEnum(RateStrategy), default=RateStrategy.STANDARD)
    status: Mapped[str]           = mapped_column(SAEnum(BookingStatus), default=BookingStatus.CONFIRMED)
    tournament_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)  # Link to tournament if applicable
    group_name: Mapped[Optional[str]]    = mapped_column(String(200), nullable=True)
    source: Mapped[Optional[str]]        = mapped_column(String(100), nullable=True)  # "direct", "OTA", "tournament"
    notes: Mapped[Optional[str]]         = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime]         = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime]         = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    room: Mapped["HotelRoom"] = relationship("HotelRoom", back_populates="reservations")

    @property
    def tid_contribution(self) -> float:
        return round(self.total_revenue * TID_RATE, 2)


class HotelRateCard(Base):
    """Date-range rate card — allows future rate planning by season/event."""
    __tablename__ = "hotel_rate_cards"

    id: Mapped[str]            = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str]          = mapped_column(String(200), nullable=False)
    start_date: Mapped[date]   = mapped_column(Date, nullable=False)
    end_date: Mapped[date]     = mapped_column(Date, nullable=False)
    strategy: Mapped[str]      = mapped_column(SAEnum(RateStrategy), nullable=False)
    multiplier: Mapped[float]  = mapped_column(Float, nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    is_active: Mapped[bool]    = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class HotelTIDLedger(Base):
    """Monthly TID assessment ledger — tracks tourism tax contributions."""
    __tablename__ = "hotel_tid_ledger"

    id: Mapped[str]                = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    month: Mapped[str]             = mapped_column(String(7), nullable=False)  # "YYYY-MM"
    room_revenue: Mapped[float]    = mapped_column(Float, nullable=False)
    tid_assessment: Mapped[float]  = mapped_column(Float, nullable=False)
    rooms_sold: Mapped[int]        = mapped_column(Integer, nullable=False)
    adr: Mapped[float]             = mapped_column(Float, nullable=False)
    occupancy_pct: Mapped[float]   = mapped_column(Float, nullable=False)
    revpar: Mapped[float]          = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime]   = mapped_column(DateTime(timezone=True), server_default=func.now())


# ── Pydantic ──────────────────────────────────────────────────────────────────

class ReservationCreate(BaseModel):
    room_id: str
    guest_name: str
    guest_email: Optional[str] = None
    guest_phone: Optional[str] = None
    check_in: date
    check_out: date
    guests: int = 1
    rate_strategy: RateStrategy = RateStrategy.STANDARD
    group_name: Optional[str] = None
    source: Optional[str] = "direct"
    tournament_id: Optional[str] = None
    notes: Optional[str] = None


class ReservationUpdate(BaseModel):
    status: Optional[BookingStatus] = None
    notes: Optional[str] = None


class RateCardCreate(BaseModel):
    name: str
    start_date: date
    end_date: date
    strategy: RateStrategy
    multiplier: float
    reason: Optional[str] = None


# ── DB dependency ─────────────────────────────────────────────────────────────

async def get_db() -> AsyncSession:
    raise NotImplementedError("Wire to your AsyncSession factory")


# ── Router ────────────────────────────────────────────────────────────────────

router = APIRouter(prefix="/api/hotel", tags=["Hotel Revenue"])
claude = Anthropic()

HOTEL_CONTEXT = """
You are the AI revenue manager for the NXS National Complex Hotel — an 85-unit property
at 704 Kirkus Street, Proctor MN 55810. Part of the NXS National Complex.
The hotel serves tournament teams, league travelers, health center guests, and regional visitors.
Phase 1 target: $1.847M/yr total complex revenue. Hotel contributes significantly.
TID (Tourism Improvement District) assessment: 1.5% of room revenue.
Duluth-Superior metro, Northeast Minnesota market. Tournament calendar drives demand spikes.
Provide specific, data-driven revenue optimization recommendations.
"""


# ── Seed ──────────────────────────────────────────────────────────────────────

@router.post("/seed", summary="Seed 85 hotel rooms, reservations, rate cards, and TID ledger")
async def seed_hotel(db: AsyncSession = Depends(get_db)) -> dict:
    existing = await db.scalar(select(func.count()).select_from(HotelRoom))
    if existing and existing > 0:
        return {"message": f"Already seeded — {existing} rooms exist", "seeded": False}

    today = date.today()
    rooms_created = []

    # Build 85 rooms across 4 floors
    room_config = [
        (RoomType.STANDARD_DOUBLE, 40, 2),
        (RoomType.STANDARD_KING,   30, 2),
        (RoomType.SUITE_KING,       8, 2),
        (RoomType.ACCESSIBLE,       5, 2),
        (RoomType.TOURNAMENT_BLOCK, 2, 4),  # larger group rooms
    ]
    room_num = 101
    for room_type, count, max_occ in room_config:
        for _ in range(count):
            floor = (room_num // 100)
            room = HotelRoom(
                room_number=str(room_num),
                room_type=room_type,
                floor=floor,
                base_rate=BASE_RATES[room_type],
                max_occupancy=max_occ,
                status=RoomStatus.AVAILABLE,
                amenities="WiFi, TV, mini-fridge, sports-view" if room_type == RoomType.SUITE_KING else "WiFi, TV",
            )
            db.add(room)
            rooms_created.append(room)
            room_num += 1
            if room_num % 100 == 26:  # wrap to next floor after 25 rooms
                room_num = (room_num // 100 + 1) * 100 + 1

    await db.flush()

    # Seed rate cards
    rate_cards = [
        RateCardCreate(name="Summer Tournament Season", start_date=today + timedelta(days=30),
                       end_date=today + timedelta(days=90), strategy=RateStrategy.TOURNAMENT, multiplier=1.35,
                       reason="Peak tournament season — high team travel demand"),
        RateCardCreate(name="Holiday Weekend", start_date=today + timedelta(days=14),
                       end_date=today + timedelta(days=17), strategy=RateStrategy.PEAK, multiplier=1.25,
                       reason="Holiday weekend premium"),
        RateCardCreate(name="Off-Peak January Rescue", start_date=today - timedelta(days=30),
                       end_date=today - timedelta(days=5), strategy=RateStrategy.RESCUE, multiplier=0.80,
                       reason="Low-season occupancy rescue pricing"),
    ]
    for rc_data in rate_cards:
        rc = HotelRateCard(**rc_data.model_dump())
        db.add(rc)

    # Seed reservations (mix of past, current, future)
    reservation_seeds = [
        # Current/recent — occupied
        {"room_idx": 0,  "guest_name": "Duluth FC Soccer Team", "check_in": today - timedelta(days=2), "check_out": today + timedelta(days=1), "guests": 2, "rate_strategy": RateStrategy.TOURNAMENT, "source": "tournament", "group_name": "Duluth FC U16"},
        {"room_idx": 1,  "guest_name": "Jensen Family",         "check_in": today - timedelta(days=1), "check_out": today + timedelta(days=2), "guests": 3, "rate_strategy": RateStrategy.STANDARD,   "source": "direct"},
        {"room_idx": 2,  "guest_name": "Essentia Health Staff", "check_in": today,                     "check_out": today + timedelta(days=3), "guests": 1, "rate_strategy": RateStrategy.GROUP,      "source": "corporate", "group_name": "Essentia Health"},
        {"room_idx": 5,  "guest_name": "MN Volleyball Club",    "check_in": today - timedelta(days=1), "check_out": today + timedelta(days=1), "guests": 4, "rate_strategy": RateStrategy.TOURNAMENT, "source": "tournament", "group_name": "MN Volleyball Club"},
        {"room_idx": 8,  "guest_name": "Thompson, Sarah",       "check_in": today,                     "check_out": today + timedelta(days=1), "guests": 2, "rate_strategy": RateStrategy.STANDARD,   "source": "OTA"},
        # Future — confirmed
        {"room_idx": 3,  "guest_name": "Iron Range Lacrosse",   "check_in": today + timedelta(days=5), "check_out": today + timedelta(days=8), "guests": 2, "rate_strategy": RateStrategy.TOURNAMENT, "source": "tournament", "group_name": "Iron Range Lacrosse Assoc"},
        {"room_idx": 4,  "guest_name": "Kowalski, David",       "check_in": today + timedelta(days=7), "check_out": today + timedelta(days=9), "guests": 2, "rate_strategy": RateStrategy.STANDARD,   "source": "direct"},
        {"room_idx": 6,  "guest_name": "Superior Basketball",   "check_in": today + timedelta(days=3), "check_out": today + timedelta(days=5), "guests": 4, "rate_strategy": RateStrategy.TOURNAMENT, "source": "tournament", "group_name": "Superior Basketball League"},
        {"room_idx": 10, "guest_name": "Magnusson, Eric",       "check_in": today + timedelta(days=12),"check_out": today + timedelta(days=14),"guests": 2, "rate_strategy": RateStrategy.STANDARD,   "source": "OTA"},
        {"room_idx": 12, "guest_name": "MN Flag Football Assoc","check_in": today + timedelta(days=20),"check_out": today + timedelta(days=23),"guests": 3, "rate_strategy": RateStrategy.TOURNAMENT, "source": "tournament", "group_name": "MN Flag Football Assoc"},
        # Past — checked out
        {"room_idx": 15, "guest_name": "Rivera, Maria",         "check_in": today - timedelta(days=10),"check_out": today - timedelta(days=8), "guests": 2, "rate_strategy": RateStrategy.STANDARD,  "source": "direct"},
        {"room_idx": 16, "guest_name": "Duluth Baseball Club",  "check_in": today - timedelta(days=14),"check_out": today - timedelta(days=11),"guests": 4, "rate_strategy": RateStrategy.TOURNAMENT, "source": "tournament", "group_name": "Duluth Baseball"},
        {"room_idx": 20, "guest_name": "Anderson, Tom",         "check_in": today - timedelta(days=7), "check_out": today - timedelta(days=5), "guests": 1, "rate_strategy": RateStrategy.RESCUE,    "source": "OTA"},
    ]

    for r_seed in reservation_seeds:
        room = rooms_created[r_seed.pop("room_idx")]
        ci = r_seed["check_in"]
        co = r_seed["check_out"]
        nights = (co - ci).days
        strategy = r_seed.get("rate_strategy", RateStrategy.STANDARD)
        rate = round(room.base_rate * STRATEGY_MULTIPLIERS[strategy], 2)
        total = round(rate * nights, 2)
        is_past = co < today
        status = BookingStatus.CHECKED_OUT if is_past else (BookingStatus.CHECKED_IN if ci <= today else BookingStatus.CONFIRMED)

        res = HotelReservation(
            room_id=room.id,
            nights=nights,
            rate_per_night=rate,
            total_revenue=total,
            status=status,
            **r_seed,
        )
        db.add(res)
        if not is_past and ci <= today:
            room.status = RoomStatus.OCCUPIED

    # Seed TID ledger — last 6 months
    for i in range(6):
        mo = today - timedelta(days=30 * (6 - i))
        mo_str = mo.strftime("%Y-%m")
        occ = 0.52 + i * 0.05 + random.uniform(-0.05, 0.05)
        occ = min(max(occ, 0.35), 0.92)
        rooms_sold = int(TOTAL_ROOMS * 30 * occ)
        base_adr = 115.0 + i * 3
        room_rev = round(rooms_sold * base_adr, 2)
        revpar = round(base_adr * occ, 2)
        tid = round(room_rev * TID_RATE, 2)
        ledger = HotelTIDLedger(
            month=mo_str, room_revenue=room_rev, tid_assessment=tid,
            rooms_sold=rooms_sold, adr=round(base_adr, 2),
            occupancy_pct=round(occ * 100, 1), revpar=revpar,
        )
        db.add(ledger)

    await db.commit()
    return {
        "message": "Hotel seeded successfully",
        "rooms": TOTAL_ROOMS,
        "reservations": len(reservation_seeds),
        "rate_cards": len(rate_cards),
        "tid_months": 6,
        "seeded": True,
    }


# ── Rooms ─────────────────────────────────────────────────────────────────────

@router.get("/rooms", summary="List all rooms with current status")
async def list_rooms(
    room_type: Optional[RoomType] = Query(None),
    status: Optional[RoomStatus] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    q = select(HotelRoom).where(HotelRoom.is_active == True)
    if room_type: q = q.where(HotelRoom.room_type == room_type)
    if status:    q = q.where(HotelRoom.status == status)
    result = await db.execute(q)
    rooms = result.scalars().all()
    return [
        {"id": r.id, "room_number": r.room_number, "room_type": r.room_type,
         "floor": r.floor, "status": r.status, "base_rate": r.base_rate,
         "max_occupancy": r.max_occupancy, "amenities": r.amenities}
        for r in rooms
    ]


# ── Occupancy ─────────────────────────────────────────────────────────────────

@router.get("/occupancy", summary="Current occupancy snapshot")
async def occupancy_snapshot(db: AsyncSession = Depends(get_db)) -> dict:
    today = date.today()
    total = await db.scalar(select(func.count()).select_from(HotelRoom).where(HotelRoom.is_active == True)) or TOTAL_ROOMS
    occupied_q = await db.execute(select(func.count()).select_from(HotelReservation).where(
        HotelReservation.check_in <= today,
        HotelReservation.check_out > today,
        HotelReservation.status.in_([BookingStatus.CONFIRMED, BookingStatus.CHECKED_IN])
    ))
    occupied = occupied_q.scalar() or 0
    occ_pct = round(occupied / total * 100, 1) if total else 0

    # Next 7 days demand
    week_out = today + timedelta(days=7)
    future_q = await db.execute(select(func.count()).select_from(HotelReservation).where(
        HotelReservation.check_in.between(today, week_out),
        HotelReservation.status == BookingStatus.CONFIRMED
    ))
    booked_next_7 = future_q.scalar() or 0

    # Revenue today (checked-in)
    rev_q = await db.execute(select(func.sum(HotelReservation.rate_per_night)).where(
        HotelReservation.check_in <= today,
        HotelReservation.check_out > today,
        HotelReservation.status.in_([BookingStatus.CONFIRMED, BookingStatus.CHECKED_IN])
    ))
    rev_today = rev_q.scalar() or 0.0

    adr = round(rev_today / occupied, 2) if occupied else 0.0
    revpar = round(rev_today / total, 2) if total else 0.0

    return {
        "date": today.isoformat(),
        "total_rooms": total,
        "occupied": occupied,
        "available": total - occupied,
        "occupancy_pct": occ_pct,
        "adr": adr,
        "revpar": revpar,
        "room_revenue_today": round(rev_today, 2),
        "tid_today": round(rev_today * TID_RATE, 2),
        "booked_next_7_days": booked_next_7,
        "occupancy_band": "HIGH" if occ_pct >= 75 else "MID" if occ_pct >= 45 else "LOW",
    }


# ── Reservations ──────────────────────────────────────────────────────────────

@router.get("/reservations", summary="List reservations with optional date range")
async def list_reservations(
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    status: Optional[BookingStatus] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    q = select(HotelReservation)
    if from_date: q = q.where(HotelReservation.check_in >= from_date)
    if to_date:   q = q.where(HotelReservation.check_out <= to_date)
    if status:    q = q.where(HotelReservation.status == status)
    q = q.order_by(HotelReservation.check_in)
    result = await db.execute(q)
    reservations = result.scalars().all()
    return [
        {"id": r.id, "room_id": r.room_id, "guest_name": r.guest_name,
         "check_in": r.check_in.isoformat(), "check_out": r.check_out.isoformat(),
         "nights": r.nights, "guests": r.guests, "rate_per_night": r.rate_per_night,
         "total_revenue": r.total_revenue, "rate_strategy": r.rate_strategy,
         "status": r.status, "source": r.source, "group_name": r.group_name,
         "tid_contribution": r.tid_contribution}
        for r in reservations
    ]


@router.post("/reservations", summary="Create a new hotel reservation")
async def create_reservation(payload: ReservationCreate, db: AsyncSession = Depends(get_db)) -> dict:
    room_result = await db.execute(select(HotelRoom).where(HotelRoom.id == payload.room_id))
    room = room_result.scalar_one_or_none()
    if not room:
        raise HTTPException(404, "Room not found")

    nights = (payload.check_out - payload.check_in).days
    if nights <= 0:
        raise HTTPException(400, "check_out must be after check_in")

    rate = round(room.base_rate * STRATEGY_MULTIPLIERS[payload.rate_strategy], 2)
    total = round(rate * nights, 2)

    res = HotelReservation(
        **payload.model_dump(),
        nights=nights,
        rate_per_night=rate,
        total_revenue=total,
    )
    db.add(res)
    await db.commit()
    await db.refresh(res)
    return {"id": res.id, "rate_per_night": rate, "total_revenue": total,
            "tid_contribution": res.tid_contribution, "message": "Reservation created"}


@router.patch("/reservations/{res_id}", summary="Update reservation status")
async def update_reservation(res_id: str, payload: ReservationUpdate, db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(select(HotelReservation).where(HotelReservation.id == res_id))
    res = result.scalar_one_or_none()
    if not res:
        raise HTTPException(404, "Reservation not found")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(res, k, v)
    await db.commit()
    return {"id": res.id, "message": "Reservation updated"}


# ── Revenue KPIs ──────────────────────────────────────────────────────────────

@router.get("/revpar", summary="RevPAR and revenue metrics — MTD and trailing 30/90 days")
async def revpar_metrics(db: AsyncSession = Depends(get_db)) -> dict:
    today = date.today()

    async def _rev_for_range(start: date, end: date) -> dict:
        q = await db.execute(select(
            func.sum(HotelReservation.total_revenue),
            func.count(HotelReservation.id),
        ).where(
            HotelReservation.check_in >= start,
            HotelReservation.check_out <= end,
            HotelReservation.status.in_([BookingStatus.CONFIRMED, BookingStatus.CHECKED_IN, BookingStatus.CHECKED_OUT]),
        ))
        row = q.one()
        rev, count = row[0] or 0.0, row[1] or 0
        nights_in_range = (end - start).days
        total_room_nights = TOTAL_ROOMS * nights_in_range
        occ_pct = round(count / total_room_nights * 100, 1) if total_room_nights else 0
        adr = round(rev / count, 2) if count else 0.0
        revpar = round(rev / total_room_nights, 2) if total_room_nights else 0.0
        return {"revenue": round(rev, 2), "reservations": count, "occupancy_pct": occ_pct,
                "adr": adr, "revpar": revpar, "tid": round(rev * TID_RATE, 2)}

    mtd_start = today.replace(day=1)
    return {
        "mtd":        await _rev_for_range(mtd_start, today),
        "trailing_30": await _rev_for_range(today - timedelta(days=30), today),
        "trailing_90": await _rev_for_range(today - timedelta(days=90), today),
        "total_rooms": TOTAL_ROOMS,
        "targets": {"annual_revenue": 1_100_000, "annual_occupancy_pct": 68.0, "target_adr": 119.0},
    }


@router.get("/tid-ledger", summary="Monthly TID assessment history")
async def tid_ledger(db: AsyncSession = Depends(get_db)) -> list[dict]:
    result = await db.execute(select(HotelTIDLedger).order_by(HotelTIDLedger.month))
    ledger = result.scalars().all()
    return [
        {"month": l.month, "room_revenue": l.room_revenue, "tid_assessment": l.tid_assessment,
         "rooms_sold": l.rooms_sold, "adr": l.adr, "occupancy_pct": l.occupancy_pct, "revpar": l.revpar}
        for l in ledger
    ]


@router.get("/rate-cards", summary="Active rate cards / seasonal pricing")
async def list_rate_cards(db: AsyncSession = Depends(get_db)) -> list[dict]:
    result = await db.execute(select(HotelRateCard).where(HotelRateCard.is_active == True).order_by(HotelRateCard.start_date))
    cards = result.scalars().all()
    return [
        {"id": c.id, "name": c.name, "start_date": c.start_date.isoformat(),
         "end_date": c.end_date.isoformat(), "strategy": c.strategy,
         "multiplier": c.multiplier, "reason": c.reason}
        for c in cards
    ]


@router.post("/rate-cards", summary="Create a rate card for a date range")
async def create_rate_card(payload: RateCardCreate, db: AsyncSession = Depends(get_db)) -> dict:
    rc = HotelRateCard(**payload.model_dump())
    db.add(rc)
    await db.commit()
    return {"message": "Rate card created"}


# ── AI Rate Recommendation ────────────────────────────────────────────────────

@router.post("/ai-rate-recommendation", summary="AI dynamic rate recommendation for next 14 days")
async def ai_rate_recommendation(db: AsyncSession = Depends(get_db)) -> dict:
    occupancy = await occupancy_snapshot(db)
    revpar = await revpar_metrics(db)

    today = date.today()
    future_res_q = await db.execute(select(HotelReservation).where(
        HotelReservation.check_in.between(today, today + timedelta(days=14)),
        HotelReservation.status == BookingStatus.CONFIRMED,
    ))
    future_res = future_res_q.scalars().all()
    future_count = len(future_res)
    tournament_bookings = sum(1 for r in future_res if r.rate_strategy == RateStrategy.TOURNAMENT)

    prompt = f"""
NXS Hotel — AI Rate Strategy Request

Current snapshot:
- Today occupancy: {occupancy['occupancy_pct']}% ({occupancy['occupied']}/{occupancy['total_rooms']} rooms)
- Today ADR: ${occupancy['adr']} | RevPAR: ${occupancy['revpar']}
- Occupancy band: {occupancy['occupancy_band']}
- Booked next 7 days: {occupancy['booked_next_7_days']} reservations

MTD performance:
- Revenue: ${revpar['mtd']['revenue']:,.0f}
- MTD occupancy: {revpar['mtd']['occupancy_pct']}%
- MTD ADR: ${revpar['mtd']['adr']} | RevPAR: ${revpar['mtd']['revpar']}
- TID generated MTD: ${revpar['mtd']['tid']:,.0f}

Next 14 days:
- Confirmed reservations: {future_count}
- Tournament-rate bookings: {tournament_bookings}
- Tournament demand share: {round(tournament_bookings/future_count*100, 1) if future_count else 0}%

Annual targets: ${revpar['targets']['annual_revenue']:,} revenue | {revpar['targets']['annual_occupancy_pct']}% occupancy | ${revpar['targets']['target_adr']} ADR

Base rates: Standard Double ${BASE_RATES[RoomType.STANDARD_DOUBLE]}/night | Standard King ${BASE_RATES[RoomType.STANDARD_KING]}/night | Suite ${BASE_RATES[RoomType.SUITE_KING]}/night

Generate a 3-paragraph rate recommendation:
1. Rate strategy for the next 14 days — should rates be raised (tournament/peak), held, or rescue-discounted? Specific recommended rates per room type.
2. Demand analysis — tournament correlation assessment, OTA vs direct booking balance, group business opportunities
3. Revenue optimization actions — specific tactics to close the gap to annual targets, promotional ideas, rescue pricing triggers
"""

    response = claude.messages.create(
        model="claude-opus-4-5",
        max_tokens=650,
        system=HOTEL_CONTEXT,
        messages=[{"role": "user", "content": prompt}],
    )

    return {
        "recommendation": response.content[0].text,
        "occupancy_snapshot": occupancy,
        "revpar_mtd": revpar["mtd"],
        "future_reservations_14d": future_count,
        "generated_at": datetime.utcnow().isoformat(),
    }


@router.post("/ai-revenue-forecast", summary="AI 90-day revenue forecast")
async def ai_revenue_forecast(db: AsyncSession = Depends(get_db)) -> dict:
    ledger = await tid_ledger(db)
    revpar = await revpar_metrics(db)

    history = "\n".join(
        f"  {l['month']}: ${l['room_revenue']:,.0f} revenue | {l['occupancy_pct']}% occ | ADR ${l['adr']} | RevPAR ${l['revpar']}"
        for l in ledger[-6:]
    )

    prompt = f"""
NXS Hotel — 90-Day Revenue Forecast

6-month history:
{history}

Current MTD: ${revpar['mtd']['revenue']:,.0f} | {revpar['mtd']['occupancy_pct']}% occupancy
Annual target: ${revpar['targets']['annual_revenue']:,}
Year-to-date gap: estimate based on trailing data

Generate a 3-paragraph 90-day forecast:
1. Projected revenue for next 90 days — month-by-month estimate with occupancy and ADR assumptions
2. Key demand drivers — which tournaments, events, and seasonal factors will move the needle
3. Risk factors and upside scenarios — what could push above or below forecast, and what rate levers to pull in each scenario
"""

    response = claude.messages.create(
        model="claude-opus-4-5",
        max_tokens=600,
        system=HOTEL_CONTEXT,
        messages=[{"role": "user", "content": prompt}],
    )

    return {
        "forecast": response.content[0].text,
        "history": ledger,
        "generated_at": datetime.utcnow().isoformat(),
    }
