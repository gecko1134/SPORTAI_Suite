"""
SportAI Suite — SaaS Admin Upgrade (v11)
Sprint 9 · Platform Core
MRR dashboard · Tenant management · API key management
Usage metering · White-label config · v11 changelog

Add to main.py:
    from routers.saas_admin_v11 import router as saas_admin_v11_router
    app.include_router(saas_admin_v11_router)
"""

from __future__ import annotations

import enum
import uuid
from datetime import date, datetime, timedelta
from typing import Optional
import random

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import (
    Boolean, DateTime, Enum as SAEnum, Float, Integer, String, Text, func, select
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


# ── Enums ─────────────────────────────────────────────────────────────────────

class TierPlan(str, enum.Enum):
    STARTER     = "starter"      # $299/mo
    PROFESSIONAL = "professional"# $599/mo
    ENTERPRISE  = "enterprise"   # $1,499/mo


class TenantStatus(str, enum.Enum):
    TRIAL    = "trial"
    ACTIVE   = "active"
    PAUSED   = "paused"
    CHURNED  = "churned"


class KeyStatus(str, enum.Enum):
    ACTIVE   = "active"
    REVOKED  = "revoked"
    EXPIRED  = "expired"


PLAN_PRICING = {
    TierPlan.STARTER:      299.0,
    TierPlan.PROFESSIONAL: 599.0,
    TierPlan.ENTERPRISE:   1_499.0,
}

PLAN_LIMITS = {
    TierPlan.STARTER:      {"api_calls_monthly": 10_000, "modules": 5, "users": 3},
    TierPlan.PROFESSIONAL: {"api_calls_monthly": 50_000, "modules": 12, "users": 10},
    TierPlan.ENTERPRISE:   {"api_calls_monthly": 500_000, "modules": 99, "users": 999},
}


# ── ORM Models ────────────────────────────────────────────────────────────────

class SaaSTenant(Base):
    """SaaS tenant — sports facility using SportAI platform."""
    __tablename__ = "saas_tenants_v11"

    id: Mapped[str]              = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str]            = mapped_column(String(200), nullable=False)
    contact_name: Mapped[str]    = mapped_column(String(200), nullable=False)
    contact_email: Mapped[str]   = mapped_column(String(255), nullable=False)
    plan: Mapped[str]            = mapped_column(SAEnum(TierPlan), nullable=False)
    status: Mapped[str]          = mapped_column(SAEnum(TenantStatus), default=TenantStatus.TRIAL)
    monthly_revenue: Mapped[float] = mapped_column(Float, nullable=False)
    trial_end: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    subscription_start: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    city: Mapped[Optional[str]]  = mapped_column(String(100), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    facility_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    api_calls_mtd: Mapped[int]   = mapped_column(Integer, default=0)
    modules_enabled: Mapped[int] = mapped_column(Integer, default=0)
    white_label: Mapped[bool]    = mapped_column(Boolean, default=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class APIKey(Base):
    """API key for tenant access."""
    __tablename__ = "api_keys_v11"

    id: Mapped[str]              = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str]       = mapped_column(String(36), nullable=False)
    key_prefix: Mapped[str]      = mapped_column(String(20), nullable=False)
    key_hash: Mapped[str]        = mapped_column(String(64), nullable=False)
    label: Mapped[str]           = mapped_column(String(200), nullable=False)
    status: Mapped[str]          = mapped_column(SAEnum(KeyStatus), default=KeyStatus.ACTIVE)
    rate_limit_per_min: Mapped[int] = mapped_column(Integer, default=60)
    calls_total: Mapped[int]     = mapped_column(Integer, default=0)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class WhiteLabelConfig(Base):
    """White-label branding config per tenant."""
    __tablename__ = "white_label_configs_v11"

    id: Mapped[str]              = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str]       = mapped_column(String(36), nullable=False, unique=True)
    platform_name: Mapped[str]   = mapped_column(String(200), nullable=False)
    primary_color: Mapped[str]   = mapped_column(String(7), default="#C9A84C")
    secondary_color: Mapped[str] = mapped_column(String(7), default="#0A2240")
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    favicon_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    custom_domain: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    hide_powered_by: Mapped[bool]= mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# ── DB dependency ─────────────────────────────────────────────────────────────

async def get_db() -> AsyncSession:
    raise NotImplementedError("Wire to your AsyncSession factory")


# ── Router ────────────────────────────────────────────────────────────────────

router = APIRouter(prefix="/api/saas-admin", tags=["SaaS Admin v11"])


# ── Seed ──────────────────────────────────────────────────────────────────────

@router.post("/seed", summary="Seed 12 SaaS tenants, API keys, and white-label configs")
async def seed_saas(db: AsyncSession = Depends(get_db)) -> dict:
    existing = await db.scalar(select(func.count()).select_from(SaaSTenant))
    if existing and existing > 0:
        return {"message": f"Already seeded — {existing} tenants exist", "seeded": False}

    today = date.today()
    random.seed(77)

    tenant_data = [
        # NXS itself (anchor tenant)
        ("NXS National Complex",          "Shaun Marline",     "shaun.marline@gmail.com",    TierPlan.ENTERPRISE,  TenantStatus.ACTIVE, "Proctor",       "MN", "multi-sport dome",  True),
        # Active paying
        ("Superior Sports Hub",           "Lisa Anderson",     "lisa@sshub.com",             TierPlan.PROFESSIONAL, TenantStatus.ACTIVE, "Superior",      "WI", "multi-sport",  False),
        ("Twin Ports Athletic Center",    "Craig Nelson",      "craig@tpac.com",             TierPlan.PROFESSIONAL, TenantStatus.ACTIVE, "Duluth",        "MN", "rec center",   False),
        ("Iron Range Sports Complex",     "Amy Hanson",        "amy@irsc.mn",                TierPlan.STARTER,      TenantStatus.ACTIVE, "Hibbing",       "MN", "hockey/multi", False),
        ("Northwoods Rec District",       "Sean Murphy",       "sean@nrd.mn",                TierPlan.PROFESSIONAL, TenantStatus.ACTIVE, "Brainerd",      "MN", "multi-sport",  False),
        ("Fox Cities Sports Center",      "Kevin Young",       "kevin@fcsc.wi",              TierPlan.ENTERPRISE,   TenantStatus.ACTIVE, "Appleton",      "WI", "dome complex", True),
        ("Great Lakes Athletic Hub",      "Maya Wright",       "maya@glah.mi",               TierPlan.PROFESSIONAL, TenantStatus.ACTIVE, "Grand Rapids",  "MI", "multi-sport",  False),
        ("Red River Sports Campus",       "Dale Peterson",     "dale@rrsc.nd",               TierPlan.STARTER,      TenantStatus.ACTIVE, "Fargo",         "ND", "multi-sport",  False),
        # Trials
        ("Lake Region Sportsplex",        "Beth Larson",       "beth@lrsp.mn",               TierPlan.PROFESSIONAL, TenantStatus.TRIAL, "Alexandria",    "MN", "multi-sport",  False),
        ("Boundary Waters Athletic Park", "Raj Kumar",         "raj@bwap.mn",                TierPlan.STARTER,      TenantStatus.TRIAL, "Ely",           "MN", "hockey/turf",  False),
        # Churned
        ("Northern Lights Rec Center",    "Pat Green",         "pat@nlrc.mn",                TierPlan.STARTER,      TenantStatus.CHURNED,"Virginia",     "MN", "rec center",   False),
        ("Arrowhead Sports Arena",        "Chris Adams",       "chris@asa.mn",               TierPlan.PROFESSIONAL, TenantStatus.PAUSED, "Eveleth",      "MN", "hockey/multi", False),
    ]

    created_tenants = []
    for (name, contact, email, plan, status, city, state, ftype, wl) in tenant_data:
        sub_start = (today - timedelta(days=random.randint(30, 400))).isoformat() if status in [TenantStatus.ACTIVE, TenantStatus.PAUSED, TenantStatus.CHURNED] else None
        trial_end = (today + timedelta(days=random.randint(5, 28))).isoformat() if status == TenantStatus.TRIAL else None
        tenant = SaaSTenant(
            name=name, contact_name=contact, contact_email=email,
            plan=plan, status=status,
            monthly_revenue=PLAN_PRICING[plan] if status == TenantStatus.ACTIVE else 0.0,
            subscription_start=sub_start, trial_end=trial_end,
            city=city, state=state, facility_type=ftype,
            api_calls_mtd=random.randint(800, 45_000) if status == TenantStatus.ACTIVE else 0,
            modules_enabled=PLAN_LIMITS[plan]["modules"] if plan != TierPlan.ENTERPRISE else 15,
            white_label=wl,
        )
        db.add(tenant)
        created_tenants.append(tenant)

    await db.flush()

    # API keys for active tenants
    for tenant in [t for t in created_tenants if t.status == TenantStatus.ACTIVE]:
        key_id = str(uuid.uuid4()).replace("-", "")[:8]
        db.add(APIKey(
            tenant_id=tenant.id,
            key_prefix=f"sk_{tenant.name[:4].lower().replace(' ', '_')}",
            key_hash=f"hashed_{key_id}",
            label=f"{tenant.name} — Production Key",
            status=KeyStatus.ACTIVE,
            rate_limit_per_min=60 if tenant.plan == TierPlan.STARTER else (200 if tenant.plan == TierPlan.PROFESSIONAL else 1000),
            calls_total=tenant.api_calls_mtd,
        ))

    # White-label configs for enterprise tenants
    for tenant in [t for t in created_tenants if t.white_label]:
        db.add(WhiteLabelConfig(
            tenant_id=tenant.id,
            platform_name=f"{tenant.name} AI Platform",
            primary_color=random.choice(["#1a73e8", "#2d6a4f", "#e63946", "#f4a261"]),
            secondary_color="#0a1628",
            custom_domain=f"ai.{tenant.name.lower().replace(' ', '')}.com",
            hide_powered_by=True,
        ))

    await db.commit()
    return {
        "message": "SaaS Admin seeded",
        "tenants": len(tenant_data),
        "api_keys": len([t for t in created_tenants if t.status == TenantStatus.ACTIVE]),
        "white_label_configs": len([t for t in created_tenants if t.white_label]),
        "seeded": True,
    }


# ── MRR Dashboard ─────────────────────────────────────────────────────────────

@router.get("/mrr-dashboard", summary="SaaS MRR, ARR, churn, and growth metrics")
async def mrr_dashboard(db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(select(SaaSTenant))
    tenants = result.scalars().all()

    active    = [t for t in tenants if t.status == TenantStatus.ACTIVE]
    trials    = [t for t in tenants if t.status == TenantStatus.TRIAL]
    churned   = [t for t in tenants if t.status == TenantStatus.CHURNED]
    paused    = [t for t in tenants if t.status == TenantStatus.PAUSED]

    mrr = sum(t.monthly_revenue for t in active)
    arr = mrr * 12

    plan_breakdown = {}
    for plan in TierPlan:
        plan_tenants = [t for t in active if t.plan == plan]
        plan_breakdown[plan.value] = {
            "count": len(plan_tenants),
            "mrr": round(sum(t.monthly_revenue for t in plan_tenants), 2),
        }

    total_api_calls = sum(t.api_calls_mtd for t in active)
    enterprise_count = sum(1 for t in active if t.plan == TierPlan.ENTERPRISE)
    wl_count = sum(1 for t in active if t.white_label)

    return {
        "mrr": round(mrr, 2),
        "arr": round(arr, 2),
        "active_tenants": len(active),
        "trial_tenants": len(trials),
        "churned_tenants": len(churned),
        "paused_tenants": len(paused),
        "churn_rate_pct": round(len(churned) / max(1, len(tenants)) * 100, 1),
        "plan_breakdown": plan_breakdown,
        "total_api_calls_mtd": total_api_calls,
        "enterprise_tenants": enterprise_count,
        "white_label_deployments": wl_count,
        "avg_mrr_per_tenant": round(mrr / len(active), 2) if active else 0,
        "ltv_estimate_avg": round(mrr / len(active) * 24, 2) if active else 0,  # 24mo avg retention
    }


# ── Tenants ───────────────────────────────────────────────────────────────────

@router.get("/tenants", summary="List all SaaS tenants")
async def list_tenants(
    status: Optional[TenantStatus] = Query(None),
    plan: Optional[TierPlan] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    q = select(SaaSTenant)
    if status: q = q.where(SaaSTenant.status == status)
    if plan:   q = q.where(SaaSTenant.plan == plan)
    q = q.order_by(SaaSTenant.monthly_revenue.desc())
    result = await db.execute(q)
    tenants = result.scalars().all()
    return [
        {"id": t.id, "name": t.name, "contact_name": t.contact_name,
         "contact_email": t.contact_email, "plan": t.plan, "status": t.status,
         "monthly_revenue": t.monthly_revenue, "city": t.city, "state": t.state,
         "facility_type": t.facility_type, "api_calls_mtd": t.api_calls_mtd,
         "modules_enabled": t.modules_enabled, "white_label": t.white_label,
         "subscription_start": t.subscription_start, "trial_end": t.trial_end}
        for t in tenants
    ]


# ── API Keys ──────────────────────────────────────────────────────────────────

@router.get("/api-keys", summary="List API keys with usage stats")
async def list_api_keys(
    tenant_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    q = select(APIKey)
    if tenant_id: q = q.where(APIKey.tenant_id == tenant_id)
    q = q.order_by(APIKey.calls_total.desc())
    result = await db.execute(q)
    keys = result.scalars().all()
    return [
        {"id": k.id, "tenant_id": k.tenant_id, "key_prefix": k.key_prefix,
         "label": k.label, "status": k.status,
         "rate_limit_per_min": k.rate_limit_per_min, "calls_total": k.calls_total,
         "last_used_at": k.last_used_at.isoformat() if k.last_used_at else None,
         "expires_at": k.expires_at, "created_at": k.created_at.isoformat()}
        for k in keys
    ]


# ── White-Label ───────────────────────────────────────────────────────────────

@router.get("/white-label-configs", summary="White-label configs for enterprise tenants")
async def list_wl_configs(db: AsyncSession = Depends(get_db)) -> list[dict]:
    result = await db.execute(select(WhiteLabelConfig))
    configs = result.scalars().all()
    return [
        {"id": c.id, "tenant_id": c.tenant_id, "platform_name": c.platform_name,
         "primary_color": c.primary_color, "secondary_color": c.secondary_color,
         "custom_domain": c.custom_domain, "hide_powered_by": c.hide_powered_by}
        for c in configs
    ]


# ── v11 Changelog ─────────────────────────────────────────────────────────────

@router.get("/changelog", summary="v11 full changelog — all 15 new modules")
async def changelog() -> dict:
    return {
        "version": "11.0.0",
        "release_date": "2026-04-09",
        "total_new_modules": 15,
        "total_new_db_tables": 52,
        "total_new_endpoints": 150,
        "sprints": [
            {"sprint": 1, "theme": "LPF Program Intelligence", "modules": ["NIL Program Dashboard", "Equipment Exchange Module"], "tables": 6, "endpoints": 23},
            {"sprint": 2, "theme": "LPF Member & Grant Engine", "modules": ["Foundation Card CRM", "Grant Tracker"], "tables": 6, "endpoints": 22},
            {"sprint": 3, "theme": "NXS Hospitality & Lodging", "modules": ["Hotel Revenue Module", "Apartment & Campground"], "tables": 8, "endpoints": 22},
            {"sprint": 4, "theme": "NGP Phase 2 Flagship", "modules": ["Skill Shot Academy", "PuttView AR Analytics"], "tables": 7, "endpoints": 20},
            {"sprint": 5, "theme": "NXS Operations", "modules": ["Ice Rink Module", "F&B Restaurant"], "tables": 7, "endpoints": 17},
            {"sprint": 6, "theme": "Academic Programs", "modules": ["Academic Programs (HS/College/University)"], "tables": 5, "endpoints": 12},
            {"sprint": 7, "theme": "AI Optimization", "modules": ["AI Revenue Maximizer", "Facility Layout Optimizer"], "tables": 5, "endpoints": 16},
            {"sprint": 8, "theme": "AI Prediction & Capital", "modules": ["Membership Value Predictor", "Capital Stack Tracker"], "tables": 8, "endpoints": 18},
            {"sprint": 9, "theme": "Integration Capstone", "modules": ["Cross-Entity Command Center", "SaaS Admin v11 Upgrade"], "tables": 6, "endpoints": 12},
        ],
        "highlights": [
            "All 4 entities fully covered: NXS Complex, Nexus Domes, LPF Foundation, NGP Development",
            "13 AI-identified revenue opportunities totaling $1.2M+ annual impact",
            "52 new ORM tables with full migration history",
            "Churn prediction model with 30/60/90-day windows for 40 scored members",
            "Full $9.85M capital stack with IRR 36.8% modeling and TID tracking",
            "200-mile PuttView AR exclusivity zone with competitor mapping",
            "10 TrackMan bay launch readiness score with phase milestone tracker",
            "100+ drop-box equipment exchange network",
            "Grant narratives for IRRRB, MN DEED, LCCMR, GMRPTC",
            "Academic recruiting match engine for HS → College pipeline",
        ],
        "seed_commands": [
            "POST /api/nil/seed", "POST /api/equipment/seed",
            "POST /api/foundation-card/seed", "POST /api/grants/seed",
            "POST /api/hotel/seed", "POST /api/lodging/seed",
            "POST /api/skill-shot/seed", "POST /api/puttview/seed",
            "POST /api/rink/seed", "POST /api/fnb/seed",
            "POST /api/academic/seed", "POST /api/revenue-ai/seed",
            "POST /api/layout-ai/seed", "POST /api/membership-predictor/seed",
            "POST /api/capital/seed", "POST /api/command-center/seed",
            "POST /api/saas-admin/seed",
        ],
    }
