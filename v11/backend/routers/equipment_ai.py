"""
SportAI Suite — Equipment Exchange AI Router
Sprint 1 · Level Playing Field Foundation
3-tier system: manufacturer partnerships, consignment (100+ drop-box network),
rental/membership plans — 8-sport inventory tracking with AI insights

Add to main.py:
    from routers.equipment_ai import router as equipment_router
    app.include_router(equipment_router)
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
    Boolean, Column, Date, DateTime, Enum as SAEnum,
    Float, ForeignKey, Integer, String, Text, func, select
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from database import get_db

class Base(DeclarativeBase):
    pass

# ── Enums ─────────────────────────────────────────────────────────────────────

class Sport(str, enum.Enum):
    FLAG_FOOTBALL = "flag_football"
    SOCCER        = "soccer"
    LACROSSE      = "lacrosse"
    VOLLEYBALL    = "volleyball"
    SOFTBALL      = "softball"
    BASKETBALL    = "basketball"
    PICKLEBALL    = "pickleball"
    ROBOTICS      = "robotics"

class EquipmentTier(str, enum.Enum):
    MANUFACTURER  = "manufacturer"   # New/donated from Nike, UA, Wilson etc.
    CONSIGNMENT   = "consignment"    # Community drop-box donations
    RENTAL        = "rental"         # Rental/membership plan inventory

class ItemCondition(str, enum.Enum):
    NEW       = "new"
    EXCELLENT = "excellent"
    GOOD      = "good"
    FAIR      = "fair"
    POOR      = "poor"

class ItemStatus(str, enum.Enum):
    AVAILABLE  = "available"
    CHECKED_OUT = "checked_out"
    RESERVED   = "reserved"
    MAINTENANCE = "maintenance"
    RETIRED    = "retired"

class TransactionType(str, enum.Enum):
    DONATION    = "donation"      # Item donated to program
    EXCHANGE    = "exchange"      # Given to youth in need
    RENTAL      = "rental"        # Rented out
    RETURN      = "return"        # Returned from rental
    CONSIGNMENT = "consignment"   # Dropped at a box location

class DropBoxStatus(str, enum.Enum):
    ACTIVE    = "active"
    FULL      = "full"
    INACTIVE  = "inactive"
    SCHEDULED = "scheduled"      # Pickup scheduled

# ── ORM Models ────────────────────────────────────────────────────────────────

class EquipmentItem(Base):
    """Individual piece of equipment in the LPF exchange inventory."""
    __tablename__ = "equipment_items"

    id: Mapped[str]              = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str]            = mapped_column(String(200), nullable=False)
    sport: Mapped[str]           = mapped_column(SAEnum(Sport), nullable=False)
    tier: Mapped[str]            = mapped_column(SAEnum(EquipmentTier), nullable=False)
    condition: Mapped[str]       = mapped_column(SAEnum(ItemCondition), nullable=False)
    status: Mapped[str]          = mapped_column(SAEnum(ItemStatus), default=ItemStatus.AVAILABLE)
    size: Mapped[Optional[str]]  = mapped_column(String(50), nullable=True)        # e.g. "Youth L", "Size 5"
    brand: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    sku: Mapped[Optional[str]]   = mapped_column(String(100), nullable=True)       # Manufacturer SKU
    retail_value: Mapped[float]  = mapped_column(Float, default=0.0)
    rental_rate: Mapped[float]   = mapped_column(Float, default=0.0)               # $/session for rental tier
    drop_box_id: Mapped[Optional[str]]  = mapped_column(ForeignKey("drop_box_locations.id"), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    received_date: Mapped[date]  = mapped_column(Date, default=date.today)
    is_active: Mapped[bool]      = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    drop_box: Mapped[Optional["DropBoxLocation"]] = relationship("DropBoxLocation", back_populates="items")
    transactions: Mapped[list["ExchangeTransaction"]] = relationship("ExchangeTransaction", back_populates="item", cascade="all, delete-orphan")

class DropBoxLocation(Base):
    """Physical drop-box location in the consignment network (100+ boxes)."""
    __tablename__ = "drop_box_locations"

    id: Mapped[str]                   = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str]                 = mapped_column(String(200), nullable=False)
    address: Mapped[str]              = mapped_column(String(500), nullable=False)
    city: Mapped[str]                 = mapped_column(String(100), nullable=False)
    state: Mapped[str]                = mapped_column(String(10), default="MN")
    zip_code: Mapped[Optional[str]]   = mapped_column(String(10), nullable=True)
    contact_name: Mapped[Optional[str]]  = mapped_column(String(200), nullable=True)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    status: Mapped[str]               = mapped_column(SAEnum(DropBoxStatus), default=DropBoxStatus.ACTIVE)
    capacity: Mapped[int]             = mapped_column(Integer, default=50)        # Max items
    sports_accepted: Mapped[str]      = mapped_column(String(500), default="all") # Comma-separated or "all"
    last_pickup_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    next_pickup_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    items_collected_ytd: Mapped[int]  = mapped_column(Integer, default=0)
    is_active: Mapped[bool]           = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime]      = mapped_column(DateTime(timezone=True), server_default=func.now())

    items: Mapped[list["EquipmentItem"]] = relationship("EquipmentItem", back_populates="drop_box")

    @property
    def current_item_count(self) -> int:
        return len([i for i in self.items if i.status == ItemStatus.AVAILABLE])

    @property
    def fill_pct(self) -> float:
        return round(self.current_item_count / self.capacity * 100, 1) if self.capacity > 0 else 0

class ExchangeTransaction(Base):
    """Tracks every movement of equipment in/out of the program."""
    __tablename__ = "exchange_transactions"

    id: Mapped[str]                      = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    item_id: Mapped[str]                 = mapped_column(ForeignKey("equipment_items.id"), nullable=False)
    transaction_type: Mapped[str]        = mapped_column(SAEnum(TransactionType), nullable=False)
    recipient_name: Mapped[Optional[str]]   = mapped_column(String(200), nullable=True)
    recipient_age: Mapped[Optional[int]]    = mapped_column(Integer, nullable=True)
    recipient_school: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    donor_name: Mapped[Optional[str]]       = mapped_column(String(200), nullable=True)
    drop_box_id: Mapped[Optional[str]]      = mapped_column(ForeignKey("drop_box_locations.id"), nullable=True)
    rental_days: Mapped[Optional[int]]      = mapped_column(Integer, nullable=True)
    rental_revenue: Mapped[float]           = mapped_column(Float, default=0.0)
    transaction_date: Mapped[date]          = mapped_column(Date, default=date.today)
    return_date: Mapped[Optional[date]]     = mapped_column(Date, nullable=True)
    notes: Mapped[Optional[str]]            = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime]            = mapped_column(DateTime(timezone=True), server_default=func.now())

    item: Mapped["EquipmentItem"] = relationship("EquipmentItem", back_populates="transactions")

# ── Pydantic Schemas ──────────────────────────────────────────────────────────

class EquipmentItemCreate(BaseModel):
    name: str
    sport: Sport
    tier: EquipmentTier
    condition: ItemCondition
    size: Optional[str] = None
    brand: Optional[str] = None
    sku: Optional[str] = None
    retail_value: float = 0.0
    rental_rate: float = 0.0
    drop_box_id: Optional[str] = None
    notes: Optional[str] = None

class DropBoxCreate(BaseModel):
    name: str
    address: str
    city: str
    state: str = "MN"
    zip_code: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    capacity: int = 50
    sports_accepted: str = "all"
    next_pickup_date: Optional[date] = None

class TransactionCreate(BaseModel):
    item_id: str
    transaction_type: TransactionType
    recipient_name: Optional[str] = None
    recipient_age: Optional[int] = None
    recipient_school: Optional[str] = None
    donor_name: Optional[str] = None
    drop_box_id: Optional[str] = None
    rental_days: Optional[int] = None
    rental_revenue: float = 0.0
    notes: Optional[str] = None

# ── Database dependency ───────────────────────────────────────────────────────

# ── Router ────────────────────────────────────────────────────────────────────

router = APIRouter(prefix="/api/equipment", tags=["Equipment Exchange"])
claude_client = Anthropic()

EQUIPMENT_CONTEXT = """
You are the AI assistant for the Level Playing Field Foundation's Equipment Exchange Program.
LPF is a 501(c)(3) nonprofit in Proctor, MN. Mission: Every Kid. Every Sport. Every Opportunity.
The Equipment Exchange operates a 3-tier system:
- Tier 1: Manufacturer partnerships (Nike, Under Armour, Wilson, etc.) — new equipment donations
- Tier 2: Consignment network — 100+ community drop-box locations across Northeast Minnesota
- Tier 3: Rental/membership plans — affordable short-term access for families
8 sports: flag football, soccer, lacrosse, volleyball, softball, basketball, pickleball, robotics.
Provide specific, actionable operational insights.
"""

# ── Seed ──────────────────────────────────────────────────────────────────────

@router.post("/seed", summary="Seed inventory, drop boxes, and sample transactions")
async def seed_equipment(db: AsyncSession = Depends(get_db)) -> dict:
    existing = await db.scalar(select(func.count()).select_from(DropBoxLocation))
    if existing and existing > 0:
        return {"message": f"Already seeded — {existing} drop boxes exist", "seeded": False}

    # Seed drop box network
    boxes_data = [
        {"name": "NXS National Complex — Main Hub",       "address": "704 Kirkus St",        "city": "Proctor",       "capacity": 200, "sports_accepted": "all"},
        {"name": "Duluth East High School",                "address": "901 Woodland Ave",     "city": "Duluth",        "capacity": 75,  "sports_accepted": "basketball,volleyball,soccer"},
        {"name": "Proctor High School",                    "address": "100 Math Cir",         "city": "Proctor",       "capacity": 60,  "sports_accepted": "all"},
        {"name": "Hermantown High School",                 "address": "4200 Ugstad Rd",       "city": "Hermantown",    "capacity": 60,  "sports_accepted": "all"},
        {"name": "Cloquet High School",                    "address": "1000 Arrowhead Blvd",  "city": "Cloquet",       "capacity": 50,  "sports_accepted": "all"},
        {"name": "YMCA Duluth",                            "address": "302 W 1st St",         "city": "Duluth",        "capacity": 80,  "sports_accepted": "basketball,volleyball,pickleball"},
        {"name": "Superior YMCA",                          "address": "4025 Tower Ave",       "city": "Superior",      "capacity": 60,  "sports_accepted": "basketball,soccer,volleyball"},
        {"name": "Duluth Central High School",             "address": "800 N Central Ave",    "city": "Duluth",        "capacity": 70,  "sports_accepted": "all"},
        {"name": "Two Harbors High School",                "address": "1640 Hwy 2",           "city": "Two Harbors",   "capacity": 40,  "sports_accepted": "soccer,softball,basketball"},
        {"name": "Esko High School",                       "address": "4886 School Rd",       "city": "Esko",          "capacity": 40,  "sports_accepted": "all"},
        {"name": "Essentia Health — Miller Hill Mall",     "address": "1600 Miller Trunk Hwy","city": "Duluth",        "capacity": 50,  "sports_accepted": "all"},
        {"name": "Fleet Farm Duluth",                      "address": "4700 Burning Tree Rd", "city": "Duluth",        "capacity": 100, "sports_accepted": "all"},
    ]

    today = date.today()
    created_boxes = []
    for b_data in boxes_data:
        box = DropBoxLocation(
            **b_data,
            last_pickup_date=today - timedelta(days=14),
            next_pickup_date=today + timedelta(days=14),
            items_collected_ytd=0,
            contact_name="LPF Volunteer Coordinator",
        )
        db.add(box)
        created_boxes.append(box)

    await db.flush()

    # Seed inventory
    main_box_id = created_boxes[0].id
    items_data = [
        # Manufacturer tier — new
        {"name": "Nike Vapor Soccer Ball",         "sport": Sport.SOCCER,        "tier": EquipmentTier.MANUFACTURER, "condition": ItemCondition.NEW,       "brand": "Nike",         "retail_value": 35.0,  "size": "Size 5"},
        {"name": "Wilson NCAA Volleyball",         "sport": Sport.VOLLEYBALL,    "tier": EquipmentTier.MANUFACTURER, "condition": ItemCondition.NEW,       "brand": "Wilson",       "retail_value": 45.0},
        {"name": "Under Armour Basketball",        "sport": Sport.BASKETBALL,    "tier": EquipmentTier.MANUFACTURER, "condition": ItemCondition.NEW,       "brand": "Under Armour", "retail_value": 50.0,  "size": "Size 29.5"},
        {"name": "Lacrosse Starter Kit",           "sport": Sport.LACROSSE,      "tier": EquipmentTier.MANUFACTURER, "condition": ItemCondition.NEW,       "brand": "Maverik",      "retail_value": 120.0, "size": "Youth L"},
        {"name": "Rawlings Softball Glove",        "sport": Sport.SOFTBALL,      "tier": EquipmentTier.MANUFACTURER, "condition": ItemCondition.NEW,       "brand": "Rawlings",     "retail_value": 65.0,  "size": "11.5\""},
        {"name": "Flag Football Set (6-player)",   "sport": Sport.FLAG_FOOTBALL, "tier": EquipmentTier.MANUFACTURER, "condition": ItemCondition.NEW,       "brand": "Baden",        "retail_value": 80.0},
        {"name": "Pickleball Paddle Set",          "sport": Sport.PICKLEBALL,    "tier": EquipmentTier.MANUFACTURER, "condition": ItemCondition.NEW,       "brand": "HEAD",         "retail_value": 55.0},
        {"name": "VEX Robotics Kit V5",            "sport": Sport.ROBOTICS,      "tier": EquipmentTier.MANUFACTURER, "condition": ItemCondition.NEW,       "brand": "VEX",          "retail_value": 350.0},
        # Consignment tier
        {"name": "Soccer Cleats",                  "sport": Sport.SOCCER,        "tier": EquipmentTier.CONSIGNMENT,  "condition": ItemCondition.GOOD,      "retail_value": 0.0,     "size": "Youth 5"},
        {"name": "Basketball Shoes",               "sport": Sport.BASKETBALL,    "tier": EquipmentTier.CONSIGNMENT,  "condition": ItemCondition.EXCELLENT,  "retail_value": 0.0,    "size": "8"},
        {"name": "Volleyball Knee Pads",           "sport": Sport.VOLLEYBALL,    "tier": EquipmentTier.CONSIGNMENT,  "condition": ItemCondition.GOOD,      "retail_value": 0.0},
        {"name": "Softball Helmet",                "sport": Sport.SOFTBALL,      "tier": EquipmentTier.CONSIGNMENT,  "condition": ItemCondition.FAIR,      "retail_value": 0.0},
        {"name": "Lacrosse Helmet",                "sport": Sport.LACROSSE,      "tier": EquipmentTier.CONSIGNMENT,  "condition": ItemCondition.GOOD,      "retail_value": 0.0,     "size": "Youth M"},
        {"name": "Basketball (worn)",              "sport": Sport.BASKETBALL,    "tier": EquipmentTier.CONSIGNMENT,  "condition": ItemCondition.FAIR,      "retail_value": 0.0,     "size": "Size 29.5"},
        # Rental tier
        {"name": "Rental Soccer Ball",             "sport": Sport.SOCCER,        "tier": EquipmentTier.RENTAL,       "condition": ItemCondition.GOOD,      "rental_rate": 3.0,      "retail_value": 30.0},
        {"name": "Rental Volleyball",              "sport": Sport.VOLLEYBALL,    "tier": EquipmentTier.RENTAL,       "condition": ItemCondition.EXCELLENT, "rental_rate": 3.0,      "retail_value": 40.0},
        {"name": "Rental Basketball",              "sport": Sport.BASKETBALL,    "tier": EquipmentTier.RENTAL,       "condition": ItemCondition.GOOD,      "rental_rate": 3.0,      "retail_value": 45.0},
        {"name": "Rental Pickleball Paddle",       "sport": Sport.PICKLEBALL,    "tier": EquipmentTier.RENTAL,       "condition": ItemCondition.EXCELLENT, "rental_rate": 5.0,      "retail_value": 50.0},
    ]

    created_items = []
    for i_data in items_data:
        item = EquipmentItem(**i_data, drop_box_id=main_box_id, received_date=today - timedelta(days=30))
        db.add(item)
        created_items.append(item)

    await db.flush()

    # Seed sample transactions
    txns = [
        {"item_id": created_items[0].id,  "transaction_type": TransactionType.EXCHANGE,    "recipient_name": "Jason M.", "recipient_age": 12, "recipient_school": "Proctor MS"},
        {"item_id": created_items[8].id,  "transaction_type": TransactionType.CONSIGNMENT, "donor_name": "Sarah K.",     "drop_box_id": created_boxes[2].id},
        {"item_id": created_items[14].id, "transaction_type": TransactionType.RENTAL,      "recipient_name": "Park Rec Team", "rental_days": 7, "rental_revenue": 21.0},
        {"item_id": created_items[1].id,  "transaction_type": TransactionType.DONATION,    "donor_name": "Wilson Sports"},
        {"item_id": created_items[3].id,  "transaction_type": TransactionType.EXCHANGE,    "recipient_name": "Alex T.", "recipient_age": 14, "recipient_school": "Duluth East"},
    ]

    for t_data in txns:
        txn = ExchangeTransaction(**t_data, transaction_date=today - timedelta(days=7))
        db.add(txn)

    # Update box YTD counts
    created_boxes[0].items_collected_ytd = 42

    await db.commit()
    return {
        "message": "Equipment Exchange seeded successfully",
        "drop_boxes": len(boxes_data),
        "inventory_items": len(items_data),
        "transactions": len(txns),
        "seeded": True,
    }

# ── Inventory ─────────────────────────────────────────────────────────────────

@router.get("/inventory", summary="List all equipment inventory")
async def list_inventory(
    sport: Optional[Sport] = Query(None),
    tier: Optional[EquipmentTier] = Query(None),
    status: Optional[ItemStatus] = Query(None),
    condition: Optional[ItemCondition] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    q = select(EquipmentItem).where(EquipmentItem.is_active == True)
    if sport:   q = q.where(EquipmentItem.sport == sport)
    if tier:    q = q.where(EquipmentItem.tier == tier)
    if status:  q = q.where(EquipmentItem.status == status)
    if condition: q = q.where(EquipmentItem.condition == condition)

    result = await db.execute(q)
    items = result.scalars().all()

    return [
        {
            "id": i.id,
            "name": i.name,
            "sport": i.sport,
            "tier": i.tier,
            "condition": i.condition,
            "status": i.status,
            "size": i.size,
            "brand": i.brand,
            "retail_value": i.retail_value,
            "rental_rate": i.rental_rate,
            "received_date": i.received_date.isoformat(),
        }
        for i in items
    ]

@router.post("/inventory", summary="Add equipment item to inventory")
async def add_item(payload: EquipmentItemCreate, db: AsyncSession = Depends(get_db)) -> dict:
    item = EquipmentItem(**payload.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return {"id": item.id, "name": item.name, "message": "Item added to inventory"}

# ── Drop Boxes ────────────────────────────────────────────────────────────────

@router.get("/dropboxes", summary="List all drop box locations with fill levels")
async def list_dropboxes(
    status: Optional[DropBoxStatus] = Query(None),
    city: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    q = select(DropBoxLocation).where(DropBoxLocation.is_active == True)
    if status: q = q.where(DropBoxLocation.status == status)
    if city:   q = q.where(DropBoxLocation.city.ilike(f"%{city}%"))

    result = await db.execute(q)
    boxes = result.scalars().unique().all()

    return [
        {
            "id": b.id,
            "name": b.name,
            "address": b.address,
            "city": b.city,
            "state": b.state,
            "status": b.status,
            "capacity": b.capacity,
            "current_items": b.current_item_count,
            "fill_pct": b.fill_pct,
            "sports_accepted": b.sports_accepted,
            "last_pickup_date": b.last_pickup_date.isoformat() if b.last_pickup_date else None,
            "next_pickup_date": b.next_pickup_date.isoformat() if b.next_pickup_date else None,
            "items_collected_ytd": b.items_collected_ytd,
        }
        for b in boxes
    ]

@router.post("/dropboxes", summary="Register a new drop box location")
async def add_dropbox(payload: DropBoxCreate, db: AsyncSession = Depends(get_db)) -> dict:
    box = DropBoxLocation(**payload.model_dump())
    db.add(box)
    await db.commit()
    await db.refresh(box)
    return {"id": box.id, "name": box.name, "message": "Drop box registered"}

# ── Transactions ──────────────────────────────────────────────────────────────

@router.post("/exchange", summary="Record an equipment transaction")
async def record_transaction(payload: TransactionCreate, db: AsyncSession = Depends(get_db)) -> dict:
    item_result = await db.execute(select(EquipmentItem).where(EquipmentItem.id == payload.item_id))
    item = item_result.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "Equipment item not found")

    txn = ExchangeTransaction(**payload.model_dump())
    db.add(txn)

    # Update item status
    if payload.transaction_type in [TransactionType.EXCHANGE]:
        item.status = ItemStatus.CHECKED_OUT
    elif payload.transaction_type == TransactionType.RENTAL:
        item.status = ItemStatus.CHECKED_OUT
    elif payload.transaction_type == TransactionType.RETURN:
        item.status = ItemStatus.AVAILABLE

    await db.commit()
    return {"id": txn.id, "message": "Transaction recorded"}

@router.get("/transactions", summary="List recent transactions")
async def list_transactions(
    transaction_type: Optional[TransactionType] = Query(None),
    days_back: int = Query(30),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    cutoff = date.today() - timedelta(days=days_back)
    q = select(ExchangeTransaction).where(ExchangeTransaction.transaction_date >= cutoff)
    if transaction_type:
        q = q.where(ExchangeTransaction.transaction_type == transaction_type)
    q = q.order_by(ExchangeTransaction.transaction_date.desc())

    result = await db.execute(q)
    txns = result.scalars().all()

    return [
        {
            "id": t.id,
            "item_id": t.item_id,
            "transaction_type": t.transaction_type,
            "recipient_name": t.recipient_name,
            "recipient_age": t.recipient_age,
            "recipient_school": t.recipient_school,
            "donor_name": t.donor_name,
            "rental_revenue": t.rental_revenue,
            "transaction_date": t.transaction_date.isoformat(),
        }
        for t in txns
    ]

# ── KPIs ──────────────────────────────────────────────────────────────────────

@router.get("/kpis", summary="Equipment Exchange KPI snapshot")
async def equipment_kpis(db: AsyncSession = Depends(get_db)) -> dict:
    total_items    = await db.scalar(select(func.count()).select_from(EquipmentItem).where(EquipmentItem.is_active == True))
    available      = await db.scalar(select(func.count()).select_from(EquipmentItem).where(EquipmentItem.status == ItemStatus.AVAILABLE))
    checked_out    = await db.scalar(select(func.count()).select_from(EquipmentItem).where(EquipmentItem.status == ItemStatus.CHECKED_OUT))
    total_boxes    = await db.scalar(select(func.count()).select_from(DropBoxLocation).where(DropBoxLocation.is_active == True))
    full_boxes     = await db.scalar(select(func.count()).select_from(DropBoxLocation).where(DropBoxLocation.status == DropBoxStatus.FULL))
    rental_rev     = await db.scalar(select(func.sum(ExchangeTransaction.rental_revenue))) or 0.0

    exchanges_q = await db.execute(select(func.count()).select_from(ExchangeTransaction).where(ExchangeTransaction.transaction_type == TransactionType.EXCHANGE))
    total_exchanges = exchanges_q.scalar()

    sports_q = await db.execute(select(EquipmentItem.sport, func.count()).where(EquipmentItem.is_active == True).group_by(EquipmentItem.sport))
    sports_breakdown = {row[0]: row[1] for row in sports_q.all()}

    tier_q = await db.execute(select(EquipmentItem.tier, func.count()).where(EquipmentItem.is_active == True).group_by(EquipmentItem.tier))
    tier_breakdown = {row[0]: row[1] for row in tier_q.all()}

    return {
        "total_items": total_items,
        "available_items": available,
        "checked_out_items": checked_out,
        "utilization_rate": round(checked_out / total_items * 100, 1) if total_items else 0,
        "active_drop_boxes": total_boxes,
        "full_drop_boxes": full_boxes,
        "total_exchanges_ytd": total_exchanges,
        "rental_revenue_total": round(rental_rev, 2),
        "sports_breakdown": sports_breakdown,
        "tier_breakdown": tier_breakdown,
    }

@router.get("/utilization", summary="Sport-by-sport utilization analysis")
async def utilization_by_sport(db: AsyncSession = Depends(get_db)) -> list[dict]:
    result = []
    for sport in Sport:
        total = await db.scalar(select(func.count()).select_from(EquipmentItem).where(EquipmentItem.sport == sport, EquipmentItem.is_active == True)) or 0
        if total == 0:
            continue
        out = await db.scalar(select(func.count()).select_from(EquipmentItem).where(EquipmentItem.sport == sport, EquipmentItem.status == ItemStatus.CHECKED_OUT)) or 0
        result.append({
            "sport": sport,
            "total_items": total,
            "checked_out": out,
            "utilization_pct": round(out / total * 100, 1) if total else 0,
        })
    return sorted(result, key=lambda x: x["utilization_pct"], reverse=True)

# ── AI Insights ───────────────────────────────────────────────────────────────

@router.post("/ai-insights", summary="AI-generated operational insights and recommendations")
async def equipment_ai_insights(db: AsyncSession = Depends(get_db)) -> dict:
    kpis = await equipment_kpis(db)
    utilization = await utilization_by_sport(db)

    # Drop boxes needing pickup
    boxes_q = await db.execute(select(DropBoxLocation).where(DropBoxLocation.is_active == True))
    boxes = boxes_q.scalars().unique().all()
    needs_pickup = [b for b in boxes if b.fill_pct >= 75 or b.status == DropBoxStatus.FULL]

    prompt = f"""
LPF Equipment Exchange current snapshot:
- Total inventory: {kpis['total_items']} items
- Available: {kpis['available_items']} | Checked out: {kpis['checked_out_items']}
- Utilization rate: {kpis['utilization_rate']}%
- Active drop boxes: {kpis['active_drop_boxes']} | Full/near-full: {len(needs_pickup)}
- Total youth served (exchanges): {kpis['total_exchanges_ytd']}
- Rental revenue: ${kpis['rental_revenue_total']:,.0f}

Sport utilization ranking:
{chr(10).join(f"  {u['sport']}: {u['utilization_pct']}% ({u['checked_out']}/{u['total_items']})" for u in utilization)}

Tier inventory breakdown: {kpis['tier_breakdown']}

Drop boxes needing pickup: {[b.name for b in needs_pickup]}

Generate 3 paragraphs:
1. Inventory health assessment — which sports/tiers are under- or over-stocked
2. Drop box network status — which boxes need immediate pickup attention and why
3. Strategic recommendations — manufacturer partners to approach, sports with highest unmet demand, rental tier expansion opportunities
"""

    response = claude_client.messages.create(
        model="claude-opus-4-5",
        max_tokens=600,
        system=EQUIPMENT_CONTEXT,
        messages=[{"role": "user", "content": prompt}],
    )

    return {
        "insights": response.content[0].text,
        "kpis_snapshot": kpis,
        "boxes_needing_pickup": [{"name": b.name, "city": b.city, "fill_pct": b.fill_pct} for b in needs_pickup],
        "generated_at": datetime.utcnow().isoformat(),
    }

@router.post("/ai-dropbox-route", summary="AI-optimized pickup route for drop box collection")
async def ai_dropbox_route(db: AsyncSession = Depends(get_db)) -> dict:
    boxes_q = await db.execute(select(DropBoxLocation).where(DropBoxLocation.is_active == True))
    boxes = boxes_q.scalars().unique().all()
    high_priority = sorted([b for b in boxes if b.fill_pct >= 50], key=lambda x: x.fill_pct, reverse=True)

    prompt = f"""
Drop box network pickup optimization for LPF Equipment Exchange.
Hub: NXS National Complex, 704 Kirkus St, Proctor MN.

Boxes by priority (fill level):
{chr(10).join(f"  {b.name} — {b.city}, MN — {b.fill_pct:.0f}% full — Last pickup: {b.last_pickup_date or 'unknown'}" for b in high_priority[:10])}

Suggest an efficient pickup route from NXS hub that minimizes driving distance while prioritizing fullest boxes.
Format as: 1. Start at hub → 2. [box name, city] → ... → Return to hub.
Include estimated total stops and why the route is ordered this way.
"""

    response = claude_client.messages.create(
        model="claude-opus-4-5",
        max_tokens=500,
        system=EQUIPMENT_CONTEXT,
        messages=[{"role": "user", "content": prompt}],
    )

    return {
        "route_recommendation": response.content[0].text,
        "high_priority_boxes": len(high_priority),
        "generated_at": datetime.utcnow().isoformat(),
    }
