# 🇮🇳 KarmSetu (कर्म सेतु)
### Cooperative-Owned Digital Service Marketplace for Labour Cooperatives
**Smart India Hackathon (SIH 2026)** | Problem Statement: Digital Operating Platform for Labour Cooperatives

---

## 📌 Executive Summary

India has over **47,182 labour cooperatives** representing **9.1+ million member workers** (*Ministry of Cooperation, 2025-26*), alongside **31.9+ crore unorganised workers** on the national e-Shram portal. Despite this organized skilled worker pool, service discovery, workforce allocation, trust verification, financial settlements, and social security coordination have remained fragmented.

**KarmSetu** is a cooperative-owned digital operating platform that bridges the gap between household / institutional service demand and verified cooperative worker pools. It transforms traditional labour cooperatives into digitally managed, highly efficient, and transparent service networks.

Unlike traditional private gig platforms, KarmSetu is built on:
1. **Explainable Smart Fair Allocation Engine**: A deterministic 6-dimension scoring engine that optimizes for skill, proximity, and fairness without black-box bias.
2. **Cooperative Revenue & Welfare Fund Split**: Enforces an 80% worker disbursement, 15% cooperative operations pool, and 5% worker welfare & insurance fund.
3. **e-Shram & Social Security Tracking**: Proactive renewal alerts for PM-SYM, PMSBY, PMJJBY, and State Labour Welfare Board schemes.
4. **Predictive Demand & Skill Gap Analytics**: Time-series seasonal forecasting that alerts cooperatives to trade deficits before demand surges.
5. **Institutional Multi-Worker Planning**: Enterprise contracts (CPWD, DMRC, hospitals) with supervisor quality inspection workflows.

---

## 🏛️ Architecture Overview

```
                          ┌──────────────────────────┐
                          │   Frontend (Next.js)     │
                          │   (To be connected)      │
                          └─────────────┬────────────┘
                                        │ REST / JSON (JWT Auth)
                          ┌─────────────▼────────────┐
                          │   FastAPI Core Backend   │
                          │   Port 8000 | /api/v1    │
                          │   Swagger UI at /docs    │
                          └─────────────┬────────────┘
                                        │
     ┌──────────────┬───────────────────┼───────────────────┬──────────────┐
     │              │                   │                   │              │
┌────▼─────┐ ┌──────▼─────┐      ┌──────▼─────┐      ┌──────▼─────┐ ┌──────▼─────┐
│   Auth   │ │Cooperative │      │ Worker     │      │ Customer   │ │  Smart     │
│  & RBAC  │ │  Operating │      │ Roster &   │      │ Bookings & │ │ Allocation │
│ (JWT+pw) │ │   System   │      │ Welfare    │      │ Lifecycle  │ │ Engine     │
└────┬─────┘ └──────┬─────┘      └──────┬─────┘      └──────┬─────┘ └──────┬─────┘
     │              │                   │                   │              │
     └──────────────┴───────────────────┼───────────────────┴──────────────┘
                                        │
     ┌──────────────┬───────────────────┼───────────────────┬──────────────┐
     │              │                   │                   │              │
┌────▼─────┐ ┌──────▼─────┐      ┌──────▼─────┐      ┌──────▼─────┐ ┌──────▼─────┐
│Settlement│ │   Demand   │      │Institu-    │      │   Audit    │ │ Realistic  │
│  Ledger  │ │Forecasting │      │  tional    │      │   Trail &  │ │ Synthetic  │
│  Engine  │ │  Analytics │      │  Projects  │      │   Reviews  │ │ Demo Data  │
└────┬─────┘ └──────┬─────┘      └──────┬─────┘      └──────┬─────┘ └──────┬─────┘
     │              │                   │                   │              │
     └──────────────┴───────────────────┼───────────────────┴──────────────┘
                                        │
                          ┌─────────────▼────────────┐
                          │  SQLite (Zero-Config)    │
                          │  or PostgreSQL/Supabase  │
                          └──────────────────────────┘
```

---

## ⚙️ Core Engines & Algorithms

### 1. Explainable Smart Fair Allocation Engine (`PRD Section 3.2`)
The core matching engine avoids opaque black-box AI and uses an explainable multi-factor scoring model:

$$\text{Score} = \text{Skill (30\%)} + \text{Availability (20\%)} + \text{Distance (15\%)} + \text{Reliability (15\%)} + \text{Workload (10\%)} + \text{Fairness (10\%)}$$

* **Hard Safety & Trade Filter**: Candidate must not be off-duty and must hold the verified mandatory trade skills.
* **Distance Proximity (15%)**: Calculated via Haversine great-circle distance between job site coordinates and worker location.
* **Fairness & Utilization Equalization (10%)**: Boosts qualified workers with lower weekly assignments to prevent income inequality within the cooperative.
* **Explainability Output**: Generates both raw numeric dimensions and human-readable AI justifications returned via API.

### 2. Time-Series Demand Forecasting & Skill-Gap Detection (`PRD Section 3`)
* Implements time-series decomposition incorporating monthly seasonal factors (e.g., monsoon plumbing spikes, summer HVAC surges, festive pre-Diwali painting demands).
* Projects forward-looking demand for 7 or 30 days with 95% confidence intervals.
* Alerts cooperative managers to impending trade deficits when projected peak demand outstrips active roster capacity.

### 3. Cooperative Financial Ledger & Welfare Fund (`PRD Section 3.3`)
Every completed job triggers an auditable ledger settlement:
* **Worker Disbursement**: ~80% directly credited to the worker's earnings ledger.
* **Cooperative Commission**: ~15% retained for cooperative operational sustainability.
* **Welfare Contribution**: ~5% deposited into the worker's dedicated social security fund (e-Shram PM-SYM, PMSBY).
* **Payment Simulation**: Supports simulation of online payments, cash-on-delivery (COD), and direct UPI reconciliations.

---

## 🚀 Quickstart Guide

### Prerequisites
* Python 3.10+ (Tested and verified on Python 3.11, 3.12, 3.13, and 3.14)
* pip & virtualenv

### 1. Clone & Setup
```bash
git clone https://github.com/arhamchhajed101/Karm-Setu.git
cd Karm-Setu

# Create and activate Python virtual environment
python -m venv .venv
# On Windows:
.\.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

### 2. Seed Realistic Demo Dataset
The built-in seeder populates **5 Cooperatives**, **214+ Verified Workers**, **95 Services**, **180 Days of Demand Observations**, and **1,050+ Historical Jobs**:
```bash
cd backend
python -m app.seed_data
```

### 3. Run Automated Pytest Suite
```bash
pytest -v tests/
```
All 14 tests verify authentication, RBAC, allocation scoring mathematics, job lifecycle transitions, settlement calculations, and forecasting.

### 4. Start the Backend Server
```bash
# Option A: From root
python run_backend.py

# Option B: Directly with uvicorn
cd backend
uvicorn app.main:app --reload --port 8000
```
* **Interactive OpenAPI Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
* **ReDoc Interactive Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
* **Health Check Probe**: [http://localhost:8000/health](http://localhost:8000/health)

### 5. Start the Frontend Application
```bash
cd frontend
npm install
npm run dev
```
* **KarmSetu Web Application**: [http://localhost:3000](http://localhost:3000)
* Built with **React + TypeScript + Tailwind CSS**
* Features **Sober Light Theme** (Civic slate, cream backgrounds, emerald verified badges)
* Custom **KarmSetu Emblem Logo** (interlocking cooperative bridge arch)
* One-click demo persona switcher for testing all 4 user roles directly from the navbar!

---

## 🔑 Pre-Seeded Demo Credentials

| Role | Email | Password | Access / Capabilities |
| :--- | :--- | :--- | :--- |
| **Cooperative Admin** | `admin@karmsetu.in` | `Password123!` | Roster management, smart allocation override, finance ledger, demand analytics |
| **Worker** | `worker@karmsetu.in` | `Password123!` | Assigned jobs, toggle availability, earnings breakdown, welfare insurance alerts |
| **Customer** | `customer@karmsetu.in` | `Password123!` | Upfront price estimate, service booking, status tracking, rating & reviews |
| **Supervisor** | `supervisor@karmsetu.in` | `Password123!` | Institutional multi-worker projects, quality inspection sign-off |

---

## 📡 API Endpoints Reference

### 🔐 Authentication & Profile (`/api/v1/auth`)
* `POST /api/v1/auth/register` — Register a customer, worker, admin, or supervisor.
* `POST /api/v1/auth/login` — Authenticate and receive JWT access token.
* `GET /api/v1/auth/me` — Retrieve current user profile with role-specific data.

### 🏢 Cooperatives & Rosters (`/api/v1/cooperatives`)
* `GET /api/v1/cooperatives` — List registered cooperatives (filter by state/district).
* `GET /api/v1/cooperatives/{id}` — Get cooperative profile & rates.
* `POST /api/v1/cooperatives` — Register a new cooperative society.
* `PUT /api/v1/cooperatives/{id}` — Update cooperative parameters.
* `GET /api/v1/cooperatives/{id}/roster` — Worker roster with availability & verification badges.
* `GET /api/v1/cooperatives/{id}/kpis` — Executive dashboard KPIs (workers, revenue, welfare pool).

### 👷 Workers (`/api/v1/workers`)
* `GET /api/v1/workers` — Filter workers by cooperative, skill, availability, verification.
* `GET /api/v1/workers/{id}` — Worker profile with ratings, certificates, and coordinates.
* `POST /api/v1/workers` — Onboard new verified worker.
* `PATCH /api/v1/workers/{id}/availability` — Toggle `AVAILABLE`, `BUSY`, or `OFF_DUTY`.
* `GET /api/v1/workers/{id}/earnings` — Itemized earnings and welfare deductions.

### 🛠️ Services Catalogue (`/api/v1/services`)
* `GET /api/v1/services` — Service offerings with category and pricing model filters.
* `GET /api/v1/services/categories` — Distinct service trade categories.
* `POST /api/v1/services` — Add new service to catalogue.

### 📋 Jobs & Estimates (`/api/v1/jobs`)
* `POST /api/v1/jobs/estimate` — Transparent upfront cost estimation.
* `POST /api/v1/jobs` — Create customer booking request.
* `GET /api/v1/jobs` — List jobs filtered by status, cooperative, worker, or customer.
* `GET /api/v1/jobs/{id}` — Job details with lifecycle timeline.
* `PATCH /api/v1/jobs/{id}/status` — Transition status (`ACCEPTED`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED`).
* `POST /api/v1/jobs/{id}/supervisor-verify` — Supervisor inspection verification.

### 🧠 Smart Fair Allocation & Explainability (`/api/v1/allocation`)
* `POST /api/v1/allocation/evaluate/{job_id}` — Run 6-dimension scoring and return ranked candidate breakdown with AI justifications.
* `POST /api/v1/allocation/auto-assign/{job_id}` — Auto-assign top-scoring candidate.
* `POST /api/v1/allocation/manual-assign/{job_id}` — Coordinator manual override with notes.

### 💰 Cooperative Settlement Ledger (`/api/v1/settlements`)
* `GET /api/v1/settlements` — Audit financial distributions.
* `POST /api/v1/settlements/simulate-payment` — Simulate payment and disburse funds.
* `GET /api/v1/settlements/cooperative/{cooperative_id}/summary` — Cooperative financial metrics.

### 🛡️ Worker Welfare & e-Shram Insurance (`/api/v1/welfare`)
* `GET /api/v1/welfare/worker/{worker_id}` — Worker social security schemes & status.
* `POST /api/v1/welfare/records` — Enroll worker into welfare scheme (PM-SYM, PMSBY).
* `GET /api/v1/welfare/alerts` — System-wide policy expiration and renewal alerts.

### 📊 Demand Forecasting & Analytics (`/api/v1/analytics`)
* `GET /api/v1/analytics/forecast` — Time-series 7d/30d projection with confidence intervals.
* `GET /api/v1/analytics/skill-gaps` — Detect trade deficits vs upcoming peak demand.
* `GET /api/v1/analytics/heatmap` — Geospatial booking density heatmap coordinates.
* `GET /api/v1/analytics/utilization/{cooperative_id}` — Fairness Gini coefficient and workload distribution.

### 🏗️ Institutional Multi-Worker Projects (`/api/v1/institutional`)
* `GET /api/v1/institutional/projects` — List enterprise/government contracts.
* `POST /api/v1/institutional/projects` — Create multi-worker contract requirement.
* `PUT /api/v1/institutional/projects/{id}` — Milestone checklist and team progress.

### ⭐ Reviews & Trust Records (`/api/v1/reviews`)
* `POST /api/v1/reviews` — Submit customer rating and review.
* `GET /api/v1/reviews/worker/{worker_id}` — List reviews for worker.

### 📜 Compliance & Audit Trail (`/api/v1/audit`)
* `GET /api/v1/audit/logs` — Query auditable system state changes.

---

## 🎨 Frontend Design & Visual Language

The frontend is built with a **sober, accessible, light civic theme** that avoids dark-mode neon/AI gimmicks, prioritizing clarity, institutional dignity, and speed:
* **Color Palette**:
  * Neutral Ground: `#F8FAFC` (soft slate white) & pure `#FFFFFF` cards with subtle `#E2E8F0` borders.
  * Typography & Accents: Deep civic slate `#1E293B` and `#334155`.
  * Trust & Verification: Emerald `#059669` / `#10B981` (Delhi police verified badges, active insurance).
  * Cooperative Accent: Warm ochre `#D97706` / `#B45309` (emblem and subtle active indicators).
* **Emblem Logo**: A custom SVG badge symbolizing cooperative labour unity: two stylized interlocking elements over an arched bridge (*Setu*).
* **Connected to Backend**: Configured via Vite proxy to route all `/api/v1` calls to the FastAPI backend seamlessly.
* **Integrated Views**:
  1. **Customer Booking Portal**: Category filters, real-time transparent estimate calculator (base price + ₹50 travel fee + emergency surge), slot picker, and state machine job tracking.
  2. **Worker Profile & Operations**: Instant availability toggle (`AVAILABLE`, `BUSY`, `OFF_DUTY`), active job queue with action buttons (`Accept`, `Start`, `Complete`), itemized earnings, and e-Shram PM-SYM / PMSBY insurance tracking.
  3. **Cooperative Admin Operating System**: Executive workforce KPIs, roster table with police verification reference IDs, **Smart Fair Allocation Inspector** (live 6-factor deterministic scoring with explainable AI justifications, auto-assign, and manual override), and settlements revenue ledger.
  4. **Demand Analytics**: Interactive 7-day Recharts forecast curves with upper/lower confidence intervals, seasonal index insights, trade deficit & skill gap alerts, and geospatial heatmap density.
  5. **Institutional Multi-Worker Projects**: Enterprise contracts (CPWD, Delhi Metro, Apollo Hospital), skills breakdown, budget disbursement, and supervisor inspection checklists.

---

## 🐳 Docker Full-Stack Deployment

```bash
docker-compose up --build
```
This builds and launches:
1. **Backend** on [http://localhost:8000](http://localhost:8000) (running seeder and FastAPI server).
2. **Frontend** on [http://localhost:3000](http://localhost:3000) (production Nginx container serving React application).

---

## ⚖️ License
Built for **Smart India Hackathon (SIH 2026)**.
