"""
SportAI Suite v11 — FastAPI Application Entry Point
NXS National Complex · 704 Kirkus St, Proctor MN 55810
Developer: Shaun Marline · NGP Development / Nexus Domes Inc.

Entities: Nexus Domes Inc. | NXS National Complex | LPF Foundation | NGP Development
v11 modules: 17 routers | 58 DB tables | 162 endpoints | 15 Alembic migrations

Usage:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

After starting: run all seed endpoints listed in /api/saas-admin/changelog
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ── v11 Routers ───────────────────────────────────────────────────────────────
from routers.nil_ai              import router as nil_router
from routers.equipment_ai        import router as equipment_router
from routers.foundation_card     import router as foundation_card_router
from routers.grant_tracker       import router as grant_router
from routers.hotel_ai            import router as hotel_router
from routers.lodging_ai          import router as lodging_router
from routers.skill_shot_ai       import router as skill_shot_router
from routers.puttview_ai         import router as puttview_router
from routers.rink_ai             import router as rink_router
from routers.fnb_ai              import router as fnb_router
from routers.academic_ai         import router as academic_router
from routers.revenue_maximizer   import router as revenue_maximizer_router
from routers.layout_ai           import router as layout_router
from routers.membership_predictor import router as membership_predictor_router
from routers.capital_stack       import router as capital_stack_router
from routers.command_center      import router as command_center_router
from routers.saas_admin_v11      import router as saas_admin_router

app = FastAPI(
    title="NXS SportAI Suite v11",
    description="Enterprise sports facility management AI — NXS National Complex, Proctor MN",
    version="11.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://*.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register all v11 routers ──────────────────────────────────────────────────
for router in [
    nil_router, equipment_router, foundation_card_router, grant_router,
    hotel_router, lodging_router, skill_shot_router, puttview_router,
    rink_router, fnb_router, academic_router, revenue_maximizer_router,
    layout_router, membership_predictor_router, capital_stack_router,
    command_center_router, saas_admin_router,
]:
    app.include_router(router)


@app.get("/", tags=["Health"])
async def root():
    return {
        "platform": "NXS SportAI Suite",
        "version": "11.0.0",
        "entity": "NXS National Complex — Proctor, MN",
        "modules": 17,
        "db_tables": 58,
        "endpoints": 162,
        "docs": "/docs",
        "changelog": "/api/saas-admin/changelog",
    }


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "version": "11.0.0"}
