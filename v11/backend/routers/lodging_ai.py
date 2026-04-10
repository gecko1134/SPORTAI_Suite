"""
SportAI Suite — Apartment & Campground Module
Sprint 3 · NXS National Complex
40-unit apartment complex + seasonal campground
Trail connections: Superior Hiking Trail, Munger State Trail, Carlton Co. snowmobile corridor

Add to main.py:
    from routers.lodging_ai import router as lodging_router
    app.include_router(lodging_router)
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
from database import get_db

class Base(DeclarativeBase):
    pass

# ── Enums ─────────────────────────────────────────────────────────────────────

class UnitType(str, enum.Enum):
    STUDIO       = "studio"
    ONE_BED      = "one_bedroom"
    TWO_BED      = "two_bedroom"
    THREE_BED    = "three_bedroom"

class LeaseStatus(str, enum.Enum):
    ACTIVE     = "active"
    EXPIRING   = "expiring"      # ≤60 days remaining
    EXPIRED    = "expired"
    VACANT     = "vacant"
    MAINTENANCE = "maintenance"

class CampSiteType(str, enum.Enum):
    TENT         = "tent"
    RV_HOOKUP    = "rv_hookup"
    CABIN        = "cabin"
    GROUP        = "group"        # Large group/team site

class Season(str, enum.Enum):
    SUMMER   = "summer"    # Jun–Aug — hiking, cycling
    FALL     = "fall"      # Sep–Oct — hiking, foliage
    WINTER   = "winter"    # Dec–Mar — snowmobile, ice fishing
    SPRING   = "spring"    # Apr–May — shoulder season

CAMP_RATES = {
    CampSiteType.TENT:      {"summer": 28.0, "fall": 24.0, "winter": 18.0, "spring": 20.0},
    CampSiteType.RV_HOOKUP: {"summer": 48.0, "fall": 42.0, "winter": 35.0, "spring": 38.0},
    CampSiteType.CABIN:     {"summer": 95.0, "fall": 80.0, "winter": 65.0, "spring": 70.0},
    CampSiteType.GROUP:     {"summer": 150.0,"fall": 120.0,"winter": 90.0, "spring": 100.0},
}

APT_BASE_RATES = {
    UnitType.STUDIO:    950.0,
    UnitType.ONE_BED:   1150.0,
    UnitType.TWO_BED:   1450.0,
    UnitType.THREE_BED: 1750.0,
}

TRAIL_CONNECTIONS = [
    {"name": "Superior Hiking Trail",         "type": "hiking",      "miles_to_trailhead": 0.4},
    {"name": "Willard Munger State Trail",    "type": "biking/hiking","miles_to_trailhead": 0.2},
    {"name": "Carlton County Snowmobile Trail","type": "snowmobile",  "miles_to_trailhead": 0.1},
    {"name": "Jay Cooke State Park",          "type": "multi-use",   "miles_to_trailhead": 2.5},
]

# ── ORM Models ────────────────────────────────────────────────────────────────

class ApartmentUnit(Base):
    """One of the 40 apartment units at NXS campus."""
    __tablename__ = "apartment_units"

    id: Mapped[str]              = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    unit_number: Mapped[str]     = mapped_column(String(10), nullable=False, unique=True)
    unit_type: Mapped[str]       = mapped_column(SAEnum(UnitType), nullable=False)
    floor: Mapped[int]           = mapped_column(Integer, nullable=False)
    sqft: Mapped[int]            = mapped_column(Integer, nullable=False)
    bedrooms: Mapped[int]        = mapped_column(Integer, nullable=False)
    bathrooms: Mapped[float]     = mapped_column(Float, nullable=False)
    monthly_rent: Mapped[float]  = mapped_column(Float, nullable=False)
    status: Mapped[str]          = mapped_column(SAEnum(LeaseStatus), default=LeaseStatus.VACANT)
    amenities: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool]      = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    leases: Mapped[list["ApartmentLease"]] = relationship("ApartmentLease", back_populates="unit", cascade="all, delete-orphan")

class ApartmentLease(Base):
    """Active or historical lease on an apartment unit."""
    __tablename__ = "apartment_leases"

    id: Mapped[str]               = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    unit_id: Mapped[str]          = mapped_column(ForeignKey("apartment_units.id"), nullable=False)
    tenant_name: Mapped[str]      = mapped_column(String(200), nullable=False)
    tenant_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    tenant_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    lease_start: Mapped[date]     = mapped_column(Date, nullable=False)
    lease_end: Mapped[date]       = mapped_column(Date, nullable=False)
    monthly_rent: Mapped[float]   = mapped_column(Float, nullable=False)
    deposit: Mapped[float]        = mapped_column(Float, nullable=False)
    is_current: Mapped[bool]      = mapped_column(Boolean, default=True)
    renewal_offered: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[Optional[str]]  = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime]  = mapped_column(DateTime(timezone=True), server_default=func.now())

    unit: Mapped["ApartmentUnit"] = relationship("ApartmentUnit", back_populates="leases")

    @property
    def days_until_expiry(self) -> int:
        return (self.lease_end - date.today()).days

    @property
    def is_expiring_soon(self) -> bool:
        return 0 < self.days_until_expiry <= 60

class CampgroundSite(Base):
    """Individual campground site on the NXS campus."""
    __tablename__ = "campground_sites"

    id: Mapped[str]              = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    site_number: Mapped[str]     = mapped_column(String(10), nullable=False, unique=True)
    site_type: Mapped[str]       = mapped_column(SAEnum(CampSiteType), nullable=False)
    max_guests: Mapped[int]      = mapped_column(Integer, nullable=False)
    has_electric: Mapped[bool]   = mapped_column(Boolean, default=False)
    has_water: Mapped[bool]      = mapped_column(Boolean, default=False)
    has_sewer: Mapped[bool]      = mapped_column(Boolean, default=False)
    is_pet_friendly: Mapped[bool]= mapped_column(Boolean, default=True)
    amenities: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool]      = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    reservations: Mapped[list["CampgroundReservation"]] = relationship("CampgroundReservation", back_populates="site", cascade="all, delete-orphan")

class CampgroundReservation(Base):
    """Campground booking — nightly stays."""
    __tablename__ = "campground_reservations"

    id: Mapped[str]              = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    site_id: Mapped[str]         = mapped_column(ForeignKey("campground_sites.id"), nullable=False)
    guest_name: Mapped[str]      = mapped_column(String(200), nullable=False)
    guest_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    check_in: Mapped[date]       = mapped_column(Date, nullable=False)
    check_out: Mapped[date]      = mapped_column(Date, nullable=False)
    nights: Mapped[int]          = mapped_column(Integer, nullable=False)
    guests: Mapped[int]          = mapped_column(Integer, default=1)
    rate_per_night: Mapped[float]= mapped_column(Float, nullable=False)
    total_revenue: Mapped[float] = mapped_column(Float, nullable=False)
    season: Mapped[str]          = mapped_column(SAEnum(Season), nullable=False)
    trail_interest: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    is_team_group: Mapped[bool]  = mapped_column(Boolean, default=False)  # NXS tournament teams
    status: Mapped[str]          = mapped_column(String(20), default="confirmed")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    site: Mapped["CampgroundSite"] = relationship("CampgroundSite", back_populates="reservations")

# ── Pydantic ──────────────────────────────────────────────────────────────────

class LeaseCreate(BaseModel):
    unit_id: str
    tenant_name: str
    tenant_email: Optional[str] = None
    tenant_phone: Optional[str] = None
    lease_start: date
    lease_end: date
    monthly_rent: float
    deposit: float
    notes: Optional[str] = None

class CampReservationCreate(BaseModel):
    site_id: str
    guest_name: str
    guest_email: Optional[str] = None
    check_in: date
    check_out: date
    guests: int = 1
    trail_interest: Optional[str] = None
    is_team_group: bool = False

def _get_season(d: date) -> Season:
    m = d.month
    if m in [6, 7, 8]:  return Season.SUMMER
    if m in [9, 10]:    return Season.FALL
    if m in [12, 1, 2, 3]: return Season.WINTER
    return Season.SPRING

# ── DB dependency ─────────────────────────────────────────────────────────────

# ── Router ────────────────────────────────────────────────────────────────────

router = APIRouter(prefix="/api/lodging", tags=["Apartments & Campground"])
claude = Anthropic()

LODGING_CONTEXT = """
You are the AI revenue manager for NXS National Complex lodging operations — Proctor, MN.
Properties: 40-unit apartment complex + seasonal campground.
Trail connections: Superior Hiking Trail, Willard Munger State Trail, Carlton County snowmobile corridor.
NXS campus: 704 Kirkus St, Proctor MN. Campground serves tournament teams, trail users, and regional visitors.
Apartments provide stable monthly revenue for the NXS complex.
Generate specific, actionable revenue and occupancy optimization insights.
"""

# ── Seed ──────────────────────────────────────────────────────────────────────

@router.post("/seed", summary="Seed 40 apartment units, leases, and campground sites + reservations")
async def seed_lodging(db: AsyncSession = Depends(get_db)) -> dict:
    existing = await db.scalar(select(func.count()).select_from(ApartmentUnit))
    if existing and existing > 0:
        return {"message": f"Already seeded — {existing} units exist", "seeded": False}

    today = date.today()

    # Build 40 apartment units
    apt_config = [
        (UnitType.STUDIO,    8, 1, 1, 480),
        (UnitType.ONE_BED,  18, 1, 1, 720),
        (UnitType.TWO_BED,  10, 2, 2, 980),
        (UnitType.THREE_BED, 4, 3, 2, 1240),
    ]
    unit_num = 101
    created_units = []
    for utype, count, beds, baths, sqft in apt_config:
        for _ in range(count):
            unit = ApartmentUnit(
                unit_number=f"A{unit_num}",
                unit_type=utype,
                floor=(unit_num - 100) // 15 + 1,
                sqft=sqft,
                bedrooms=beds,
                bathrooms=baths,
                monthly_rent=APT_BASE_RATES[utype],
                status=LeaseStatus.VACANT,
                amenities="In-unit washer/dryer, NXS facility access, trail proximity",
            )
            db.add(unit)
            created_units.append(unit)
            unit_num += 1

    await db.flush()

    # Seed leases — 34 of 40 occupied (85% occupancy)
    tenant_names = [
        "Rivera Family", "Kowalski, Jake", "Thompson, Carla", "Anderson, Brian",
        "Magnusson, Elsa", "Okafor, Imani", "Patel Family", "Williams, Jordan",
        "Gustafson, Nathan", "Torres, Angela", "Lindqvist, Sven", "Diallo, Amara",
        "Johnson, Marcus", "Brooks, Priya", "Carter, Elijah", "West, Carla",
        "Nilsson, Erik", "Sanchez Family", "Kumar, Raj", "Oberg, Rachel",
        "Larson, Beth", "Nelson, Craig", "Hanson, Amy", "Peterson, Dale",
        "Murphy, Sean", "Baker, Lisa", "Young, Kevin", "Wright, Maya",
        "Hall, Steve", "Allen, Tanya", "King, Robert", "Scott, Jennifer",
        "Adams, Chris", "Green, Pat",
    ]

    lease_start_base = today - timedelta(days=180)
    for i, tenant in enumerate(tenant_names):
        unit = created_units[i]
        ls = lease_start_base + timedelta(days=i * 5)
        le = ls + timedelta(days=365)
        days_left = (le - today).days
        status = LeaseStatus.EXPIRING if days_left <= 60 else LeaseStatus.ACTIVE
        unit.status = status
        lease = ApartmentLease(
            unit_id=unit.id, tenant_name=tenant,
            tenant_email=f"{tenant.lower().replace(', ','_').replace(' ','_')}@email.com",
            lease_start=ls, lease_end=le,
            monthly_rent=unit.monthly_rent,
            deposit=unit.monthly_rent * 1.5,
            renewal_offered=status == LeaseStatus.EXPIRING,
            is_current=True,
        )
        db.add(lease)

    await db.flush()

    # Campground — build 30 sites
    site_config = [
        (CampSiteType.TENT,      12, False, False, False, 6,  "Fire ring, picnic table"),
        (CampSiteType.RV_HOOKUP,  8, True,  True,  False, 6,  "Full hookup, picnic table, fire ring"),
        (CampSiteType.RV_HOOKUP,  4, True,  True,  True,  6,  "Full hookup with sewer, premium"),
        (CampSiteType.CABIN,      4, True,  True,  True,  4,  "Heated cabin, kitchenette, NXS access"),
        (CampSiteType.GROUP,      2, True,  True,  False, 20, "Large team site, multi-vehicle, pavilion"),
    ]
    site_num = 1
    created_sites = []
    for stype, count, elec, water, sewer, max_g, amen in site_config:
        for _ in range(count):
            site = CampgroundSite(
                site_number=f"C{site_num:02d}",
                site_type=stype, max_guests=max_g,
                has_electric=elec, has_water=water, has_sewer=sewer,
                amenities=amen, is_pet_friendly=True,
            )
            db.add(site)
            created_sites.append(site)
            site_num += 1

    await db.flush()

    # Campground reservations
    camp_seeds = [
        {"site_idx": 0,  "guest_name": "Lindberg Family",      "check_in": today - timedelta(days=5), "check_out": today - timedelta(days=2), "guests": 4, "trail_interest": "Superior Hiking Trail"},
        {"site_idx": 1,  "guest_name": "Smith, Ron (RV)",      "check_in": today - timedelta(days=3), "check_out": today + timedelta(days=2), "guests": 2, "trail_interest": "Munger State Trail"},
        {"site_idx": 14, "guest_name": "Duluth Volleyball Club","check_in": today - timedelta(days=1), "check_out": today + timedelta(days=1), "guests": 12, "is_team_group": True},
        {"site_idx": 2,  "guest_name": "Anderson Camping Trip", "check_in": today + timedelta(days=3), "check_out": today + timedelta(days=6), "guests": 4, "trail_interest": "Jay Cooke State Park"},
        {"site_idx": 10, "guest_name": "Snowmobile Group MN",  "check_in": today + timedelta(days=10),"check_out": today + timedelta(days=13),"guests": 6, "trail_interest": "Carlton County Snowmobile Trail"},
        {"site_idx": 3,  "guest_name": "Peterson, Dale",       "check_in": today + timedelta(days=7), "check_out": today + timedelta(days=9), "guests": 2},
        {"site_idx": 15, "guest_name": "Iron Range Soccer Team","check_in": today + timedelta(days=5), "check_out": today + timedelta(days=7), "guests": 18, "is_team_group": True},
    ]

    for seed in camp_seeds:
        site = created_sites[seed.pop("site_idx")]
        ci = seed["check_in"]
        co = seed["check_out"]
        nights = (co - ci).days
        season = _get_season(ci)
        rate = CAMP_RATES[site.site_type][season.value]
        camp_res = CampgroundReservation(
            site_id=site.id,
            nights=nights,
            rate_per_night=rate,
            total_revenue=round(rate * nights, 2),
            season=season,
            **{k: v for k, v in seed.items() if k not in ["check_in", "check_out"]},
            check_in=ci, check_out=co,
        )
        db.add(camp_res)

    await db.commit()
    return {
        "message": "Lodging module seeded",
        "apartment_units": 40,
        "leases": len(tenant_names),
        "occupancy_rate": f"{len(tenant_names)/40*100:.0f}%",
        "campground_sites": site_num - 1,
        "camp_reservations": len(camp_seeds),
        "seeded": True,
    }

# ── Apartments ────────────────────────────────────────────────────────────────

@router.get("/apartments", summary="List all apartment units with lease status")
async def list_apartments(
    unit_type: Optional[UnitType] = Query(None),
    status: Optional[LeaseStatus] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    q = select(ApartmentUnit).where(ApartmentUnit.is_active == True)
    if unit_type: q = q.where(ApartmentUnit.unit_type == unit_type)
    if status:    q = q.where(ApartmentUnit.status == status)
    result = await db.execute(q)
    units = result.scalars().unique().all()
    return [
        {"id": u.id, "unit_number": u.unit_number, "unit_type": u.unit_type,
         "floor": u.floor, "sqft": u.sqft, "bedrooms": u.bedrooms,
         "bathrooms": u.bathrooms, "monthly_rent": u.monthly_rent, "status": u.status,
         "amenities": u.amenities}
        for u in units
    ]

@router.get("/leases", summary="List current leases with expiry info")
async def list_leases(
    expiring_soon: bool = Query(False),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    q = select(ApartmentLease).where(ApartmentLease.is_current == True)
    result = await db.execute(q)
    leases = result.scalars().all()
    if expiring_soon:
        leases = [l for l in leases if l.is_expiring_soon]
    return [
        {"id": l.id, "unit_id": l.unit_id, "tenant_name": l.tenant_name,
         "lease_start": l.lease_start.isoformat(), "lease_end": l.lease_end.isoformat(),
         "monthly_rent": l.monthly_rent, "days_until_expiry": l.days_until_expiry,
         "is_expiring_soon": l.is_expiring_soon, "renewal_offered": l.renewal_offered}
        for l in leases
    ]

@router.post("/leases", summary="Create a new lease")
async def create_lease(payload: LeaseCreate, db: AsyncSession = Depends(get_db)) -> dict:
    unit_result = await db.execute(select(ApartmentUnit).where(ApartmentUnit.id == payload.unit_id))
    unit = unit_result.scalar_one_or_none()
    if not unit:
        raise HTTPException(404, "Unit not found")
    lease = ApartmentLease(**payload.model_dump())
    unit.status = LeaseStatus.ACTIVE
    db.add(lease)
    await db.commit()
    return {"message": "Lease created"}

@router.get("/rent-roll", summary="Monthly rent roll summary")
async def rent_roll(db: AsyncSession = Depends(get_db)) -> dict:
    total_q = await db.execute(select(func.count(), func.sum(ApartmentUnit.monthly_rent)).where(ApartmentUnit.is_active == True))
    total_row = total_q.one()
    total_units, potential_monthly = total_row[0], total_row[1] or 0.0

    occupied_q = await db.execute(select(func.count(), func.sum(ApartmentLease.monthly_rent)).where(ApartmentLease.is_current == True))
    occ_row = occupied_q.one()
    occupied, actual_monthly = occ_row[0], occ_row[1] or 0.0

    expiring_q = await db.execute(select(func.count()).select_from(ApartmentLease).where(ApartmentLease.is_current == True))
    leases = (await db.execute(select(ApartmentLease).where(ApartmentLease.is_current == True))).scalars().all()
    expiring_soon = sum(1 for l in leases if l.is_expiring_soon)

    type_q = await db.execute(select(ApartmentUnit.unit_type, func.count(), func.sum(ApartmentUnit.monthly_rent)).where(ApartmentUnit.is_active == True).group_by(ApartmentUnit.unit_type))
    type_breakdown = {row[0]: {"units": row[1], "potential_monthly": round(row[2] or 0, 2)} for row in type_q.all()}

    return {
        "total_units": total_units,
        "occupied_units": occupied,
        "vacant_units": total_units - occupied,
        "occupancy_rate": round(occupied / total_units * 100, 1) if total_units else 0,
        "actual_monthly_revenue": round(actual_monthly, 2),
        "potential_monthly_revenue": round(potential_monthly, 2),
        "annual_actual": round(actual_monthly * 12, 2),
        "annual_potential": round(potential_monthly * 12, 2),
        "vacancy_loss_monthly": round(potential_monthly - actual_monthly, 2),
        "leases_expiring_60d": expiring_soon,
        "type_breakdown": type_breakdown,
    }

# ── Campground ────────────────────────────────────────────────────────────────

@router.get("/campground", summary="List all campground sites")
async def list_campground(
    site_type: Optional[CampSiteType] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    q = select(CampgroundSite).where(CampgroundSite.is_active == True)
    if site_type: q = q.where(CampgroundSite.site_type == site_type)
    result = await db.execute(q)
    sites = result.scalars().all()
    return [
        {"id": s.id, "site_number": s.site_number, "site_type": s.site_type,
         "max_guests": s.max_guests, "has_electric": s.has_electric,
         "has_water": s.has_water, "has_sewer": s.has_sewer,
         "is_pet_friendly": s.is_pet_friendly, "amenities": s.amenities,
         "rates": CAMP_RATES[s.site_type]}
        for s in sites
    ]

@router.post("/campground/reserve", summary="Create a campground reservation")
async def reserve_campsite(payload: CampReservationCreate, db: AsyncSession = Depends(get_db)) -> dict:
    site_result = await db.execute(select(CampgroundSite).where(CampgroundSite.id == payload.site_id))
    site = site_result.scalar_one_or_none()
    if not site:
        raise HTTPException(404, "Site not found")
    nights = (payload.check_out - payload.check_in).days
    season = _get_season(payload.check_in)
    rate = CAMP_RATES[site.site_type][season.value]
    res = CampgroundReservation(
        site_id=payload.site_id,
        guest_name=payload.guest_name,
        guest_email=payload.guest_email,
        check_in=payload.check_in,
        check_out=payload.check_out,
        nights=nights,
        guests=payload.guests,
        rate_per_night=rate,
        total_revenue=round(rate * nights, 2),
        season=season,
        trail_interest=payload.trail_interest,
        is_team_group=payload.is_team_group,
    )
    db.add(res)
    await db.commit()
    return {"id": res.id, "rate_per_night": rate, "total_revenue": res.total_revenue,
            "season": season, "message": "Campsite reserved"}

@router.get("/campground/reservations", summary="Upcoming campground reservations")
async def campground_reservations(
    days_ahead: int = Query(30),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    today = date.today()
    result = await db.execute(select(CampgroundReservation).where(
        CampgroundReservation.check_in >= today,
        CampgroundReservation.check_in <= today + timedelta(days=days_ahead),
    ).order_by(CampgroundReservation.check_in))
    reservations = result.scalars().all()
    return [
        {"id": r.id, "site_id": r.site_id, "guest_name": r.guest_name,
         "check_in": r.check_in.isoformat(), "check_out": r.check_out.isoformat(),
         "nights": r.nights, "guests": r.guests, "rate_per_night": r.rate_per_night,
         "total_revenue": r.total_revenue, "season": r.season,
         "trail_interest": r.trail_interest, "is_team_group": r.is_team_group}
        for r in reservations
    ]

@router.get("/campground/seasonal-rates", summary="Campground rates by site type and season")
async def seasonal_rates() -> dict:
    return {
        "rates": {st.value: CAMP_RATES[st] for st in CampSiteType},
        "trail_connections": TRAIL_CONNECTIONS,
        "seasons": {
            "summer": "Jun–Aug | Hiking, cycling, paddling",
            "fall":   "Sep–Oct | Foliage, hiking, hunting",
            "winter": "Dec–Mar | Snowmobile, ice fishing, cross-country ski",
            "spring": "Apr–May | Shoulder season, trail opening",
        }
    }

# ── Revenue Rollup ────────────────────────────────────────────────────────────

@router.get("/revenue-rollup", summary="Combined apartment + campground revenue summary")
async def revenue_rollup(db: AsyncSession = Depends(get_db)) -> dict:
    rent = await rent_roll(db)

    camp_rev_q = await db.execute(select(func.sum(CampgroundReservation.total_revenue)))
    camp_rev = camp_rev_q.scalar() or 0.0

    camp_count_q = await db.execute(select(func.count()).select_from(CampgroundReservation))
    camp_count = camp_count_q.scalar() or 0

    today = date.today()
    camp_upcoming_q = await db.execute(select(func.sum(CampgroundReservation.total_revenue)).where(
        CampgroundReservation.check_in >= today
    ))
    camp_upcoming = camp_upcoming_q.scalar() or 0.0

    return {
        "apartments": {
            "monthly_revenue": rent["actual_monthly_revenue"],
            "annual_revenue": rent["annual_actual"],
            "occupancy_rate": rent["occupancy_rate"],
            "leases_expiring_60d": rent["leases_expiring_60d"],
            "vacancy_loss_monthly": rent["vacancy_loss_monthly"],
        },
        "campground": {
            "total_revenue_all_time": round(camp_rev, 2),
            "total_reservations": camp_count,
            "upcoming_revenue": round(camp_upcoming, 2),
            "trail_connections": len(TRAIL_CONNECTIONS),
        },
        "combined": {
            "monthly_lodging_revenue": round(rent["actual_monthly_revenue"] + (camp_rev / 12), 2),
            "annual_lodging_estimate": round(rent["annual_actual"] + camp_rev, 2),
        }
    }

# ── AI Insights ───────────────────────────────────────────────────────────────

@router.post("/ai-insights", summary="AI lodging optimization brief — apartments + campground")
async def lodging_ai_insights(db: AsyncSession = Depends(get_db)) -> dict:
    rent = await rent_roll(db)
    rollup = await revenue_rollup(db)
    leases_expiring = await list_leases(expiring_soon=True, db=db)

    prompt = f"""
NXS Lodging Operations — Combined Optimization Brief

APARTMENTS (40 units):
- Occupancy: {rent['occupancy_rate']}% ({rent['occupied_units']}/{rent['total_units']})
- Monthly actual revenue: ${rent['actual_monthly_revenue']:,.0f}
- Annual actual: ${rent['annual_actual']:,.0f}
- Annual potential (full occupancy): ${rent['annual_potential']:,.0f}
- Monthly vacancy loss: ${rent['vacancy_loss_monthly']:,.0f}
- Leases expiring in 60 days: {rent['leases_expiring_60d']}
- Unit mix: {rent['type_breakdown']}

CAMPGROUND (30 sites):
- Trail connections: Superior Hiking Trail (0.4mi), Munger State Trail (0.2mi), Carlton Co. Snowmobile (0.1mi)
- Current season rates: Tent ${CAMP_RATES[CampSiteType.TENT]} | RV hookup ${CAMP_RATES[CampSiteType.RV_HOOKUP]} | Cabin ${CAMP_RATES[CampSiteType.CABIN]}/night
- Upcoming revenue booked: ${rollup['campground']['upcoming_revenue']:,.0f}
- Tournament team groups: key demand driver

Tenants with expiring leases: {[l['tenant_name'] for l in leases_expiring[:5]]}

Generate a 3-paragraph lodging strategy brief:
1. Apartment occupancy health — assess vacancy loss, renewal urgency, and unit-mix demand (which sizes move fastest)
2. Campground revenue opportunity — seasonal demand peaks, trail-connected marketing angles, tournament team group packages
3. Combined lodging strategy — how to package apartment + campground + hotel into a regional sports tourism lodging play, corporate housing pitch, and targeted outreach for next 90 days
"""

    response = claude.messages.create(
        model="claude-opus-4-5",
        max_tokens=700,
        system=LODGING_CONTEXT,
        messages=[{"role": "user", "content": prompt}],
    )

    return {
        "insights": response.content[0].text,
        "rent_roll": rent,
        "revenue_rollup": rollup,
        "trail_connections": TRAIL_CONNECTIONS,
        "generated_at": datetime.utcnow().isoformat(),
    }
