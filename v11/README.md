# NXS SportAI Suite — v11.0.0

**Enterprise sports facility management AI platform**
NXS National Complex · 704 Kirkus St, Proctor MN 55810
Developer: Shaun Marline | NGP Development / Nexus Domes Inc.

---

## 4 Entities Covered

| Entity | Type | Focus |
|--------|------|-------|
| Nexus Domes Inc. | For-profit LLC | Operating company, memberships, sponsorships |
| NXS National Complex | Facility | 223,500 sqft indoor · Hotel · Rink · F&B |
| Level Playing Field Foundation | 501(c)(3) | NIL, equipment exchange, scholarships, grants |
| NGP Development | Real estate | $9.85M capital stack · IRR 36.8% · Payback 3.1yr |

---

## v11 Modules (17 Routers)

| Sprint | Module | Prefix |
|--------|--------|--------|
| S1 | NIL Program Dashboard | `/api/nil` |
| S1 | Equipment Exchange | `/api/equipment` |
| S2 | Foundation Card CRM | `/api/foundation-card` |
| S2 | Grant Tracker | `/api/grants` |
| S3 | Hotel Revenue Module | `/api/hotel` |
| S3 | Apartment & Campground | `/api/lodging` |
| S4 | Skill Shot Academy | `/api/skill-shot` |
| S4 | PuttView AR Analytics | `/api/puttview` |
| S5 | Ice Rink Module | `/api/rink` |
| S5 | F&B Restaurant | `/api/fnb` |
| S6 | Academic Programs | `/api/academic` |
| S7 | AI Revenue Maximizer | `/api/revenue-ai` |
| S7 | Facility Layout Optimizer | `/api/layout-ai` |
| S8 | Membership Value Predictor | `/api/membership-predictor` |
| S8 | Capital Stack Tracker | `/api/capital` |
| S9 | Cross-Entity Command Center | `/api/command-center` |
| S9 | SaaS Admin v11 | `/api/saas-admin` |

---

## Quick Start

### Backend
```bash
cd v11/backend
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql+asyncpg://user:pass@localhost/sportai_v11"
export ANTHROPIC_API_KEY="sk-ant-..."

# Run migrations
alembic upgrade head

# Start server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd v11/frontend
npm install
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

### Seed all modules (in order)
```bash
BASE=http://localhost:8000
for endpoint in nil equipment foundation-card grants hotel lodging \
  skill-shot puttview rink fnb academic revenue-ai layout-ai \
  membership-predictor capital command-center saas-admin; do
  curl -X POST $BASE/api/$endpoint/seed
  echo "✓ $endpoint seeded"
done
```

---

## Database

- **ORM:** SQLAlchemy 2.0 async
- **Driver:** asyncpg (PostgreSQL)
- **Migrations:** Alembic (migrations 007–015 in `backend/alembic/versions/`)
- **New tables in v11:** 58
- **Total endpoints:** 162

---

## Key Financial Targets

| Metric | Target |
|--------|--------|
| Phase 1 Annual Revenue | $1.847M |
| Phase 2 Skill Shot Year 1 | $3.8M |
| PuttView AR Annual | $153K (137% ROI) |
| Capital Pipeline | $9.85M |
| 5-Year Combined Revenue | $35.6M |
| IRR | 36.8% |
| Payback Period | 3.1 years |

---

## Frontend Pages

All pages use the dark sports-tech aesthetic: electric gold (`#C9A84C`) + navy (`#0A2240`), Bebas Neue + Barlow Condensed typefaces.

Located in `v11/frontend/app/` — one `page.tsx` per module.

---

*ISG Engineering Project #24688001 · Level Playing Field Foundation · levelplayingfieldfoundation.org*
