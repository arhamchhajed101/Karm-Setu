[KarmSetu_README.md](https://github.com/user-attachments/files/31889625/KarmSetu_README.md)
# KarmSetu (कर्म सेतु)

**Smart India Hackathon 2026** — Problem Statement: Digital Operating Platform for Labour Cooperatives

Live demo: https://arhamchhajed101.github.io/Karm-Setu/

Built with FastAPI + Python on the backend and React + TypeScript on the frontend.

---

## What is KarmSetu?

KarmSetu is a digital operating layer for labour cooperatives — the kind of organizations where a group of skilled workers (electricians, plumbers, masons, painters, welders) come together under a registered cooperative society to find and complete work as a group, instead of individually.

Right now, most of that coordination happens over phone calls and a coordinator's memory. KarmSetu doesn't try to replace the cooperative or the workers — it gives the cooperative a system to run itself: who's available, who gets assigned to what, how payments and welfare contributions are tracked, and roughly how much work to expect next month.

We're not building "Uber for plumbers." The difference matters: in a gig marketplace, the platform owns the customer and treats workers as independent contractors. In KarmSetu, the cooperative stays the employer and keeps ownership of the relationship with both its workers and its customers — we're just the software layer underneath.

## The problem we're actually solving

India has a large, real cooperative movement — well over 6.5 lakh functional cooperative societies nationally across all sectors, and cooperatives specifically built around organizing skilled labour (like the Uralungal Labour Contract Cooperative Society in Kerala, which employs 13,500+ workers and takes on large government contracts) are a recognized, federated part of that movement.

But the operational side hasn't kept up. The government's own PACS computerization push has digitized loan books and membership records for tens of thousands of societies — that's a real and valuable effort, but it's about accounting, not about day-to-day workforce coordination. There's no equivalent system for the actual work: figuring out who's free, matching them fairly to a job, tracking whether the job got done, and settling payment afterward.

That gap creates three different problems depending on who you ask:
- **Workers** get irregular, word-of-mouth opportunities and have no record of their own earnings, ratings, or reliability.
- **Cooperatives** are stuck coordinating everything by phone and can't credibly bid for larger institutional contracts because they have no systematic way to plan or track a bigger workforce.
- **Customers and institutions** have no way to verify who they're actually getting, or hold anyone accountable if something goes wrong.

(We're being careful here not to overstate this — we're not claiming worker exploitation or harm happens *because* KarmSetu doesn't exist. The evidence is about a coordination gap, not a causal story. Full sourcing for every claim in this section is in `docs/RESEARCH.md`.)

## Our solution

KarmSetu gives a cooperative four things it doesn't currently have:

1. A **worker roster** with verified skills, certificates, and live availability.
2. A **fair allocation engine** that assigns jobs by skill match, distance, current workload, and reliability — using a transparent scoring formula the cooperative can actually see and question, not a black box.
3. A **settlement ledger** that splits every completed job's payment automatically (80% to the worker, 15% to cooperative operations, 5% to a welfare fund) and keeps a record of it.
4. **Demand forecasting** based on the cooperative's own booking history, so they can see a seasonal spike (say, painting demand before Diwali) coming before it hits.

## What we think is the actual innovation here

Honestly, none of these four pieces is individually novel — allocation algorithms and demand forecasting are well-studied problems (there's actual literature on fair, skill-constrained workforce scheduling that we leaned on for the allocation engine's design — see `docs/RESEARCH.md`). The part we think matters is *who owns the platform*: it's built cooperative-first, not customer-first. The cooperative keeps its members, its customer relationships, and its revenue split — KarmSetu is infrastructure it runs, not a middleman it depends on.

We also went out of our way to keep the "AI" parts of this honest. The allocation engine is a deterministic, explainable scoring formula — every score can be broken down into the exact numbers that produced it. The forecasting engine is a statistical seasonal model on real booking data, not a trained machine learning model — we didn't have the data volume in a hackathon timeframe to honestly claim that, so we're not claiming it.

## Main features

- Customer-facing booking flow with upfront cost estimates and live job status tracking
- Worker dashboard: toggle availability, accept/start/complete jobs, see itemized earnings
- Cooperative admin dashboard: roster management, the allocation engine (with manual override), and a revenue ledger
- Institutional/enterprise view for multi-worker, multi-site contracts (e.g. a municipality needing 50 electricians across 5 locations)
- Analytics dashboard with a 7/30-day demand forecast, skill-gap alerts, and workforce utilization stats
- Welfare tracking with renewal reminders for schemes like e-Shram, PM-SYM, PMSBY, and PMJJBY — note this is a reminder system based on dates the cooperative enters, not a live integration with those government portals
- Ratings and review history per worker
- Audit log for settlement and status-change events

## Tech stack

**Backend:** Python, FastAPI, SQLAlchemy, JWT-based auth, pytest (14 tests covering auth, allocation scoring, job lifecycle, and settlement math)

**Frontend:** React + TypeScript, Vite, Tailwind CSS

**Data:** SQLite by default (zero config), swappable for PostgreSQL

**Deployment:** Docker Compose for local full-stack; `render.yaml` blueprint and `frontend/vercel.json` for hosting

## System architecture

```
        React + TypeScript frontend (Vite, Tailwind)
                        │
              REST / JSON, JWT auth
                        │
        FastAPI backend  —  /api/v1  (Swagger docs at /docs)
                        │
   ┌───────────┬────────┼────────┬───────────┐
Auth & RBAC  Allocation  Forecasting  Settlement  Audit
             Engine      Engine       Engine      Service
   └───────────┴────────┼────────┴───────────┘
                        │
              SQLAlchemy models → SQLite / PostgreSQL
```

The frontend talks to the backend over a REST API secured with JWTs. The backend is organized into services rather than one big file: allocation, forecasting, and settlement each live in their own module under `backend/app/services/`, which made it a lot easier to test them independently (see `backend/tests/`).

## Setup & running it locally

**Prerequisites:** Python 3.10+, Node.js (for the frontend), pip

**1. Clone and set up the backend**
```bash
git clone https://github.com/arhamchhajed101/Karm-Setu.git
cd Karm-Setu

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r backend/requirements.txt
```

**2. Seed demo data**

This populates 5 cooperatives, ~214 workers, 95 service listings, 180 days of demand history, and just over 1,050 historical jobs, so the app doesn't look empty on first run:
```bash
cd backend
python -m app.seed_data
```

**3. Run the tests** (optional, but a good sanity check)
```bash
pytest -v tests/
```

**4. Start the backend**
```bash
python run_backend.py
# or: cd backend && uvicorn app.main:app --reload --port 8000
```
API docs: http://localhost:8000/docs · Health check: http://localhost:8000/health

**5. Start the frontend**
```bash
cd frontend
npm install
npm run dev
```
App: http://localhost:3000 — there's a persona switcher in the navbar to jump between the Customer, Worker, Cooperative Admin, and Supervisor views without logging in and out repeatedly.

**Or, run everything with Docker:**
```bash
docker-compose up --build
```

### Demo login credentials

| Role | Email | Password |
|---|---|---|
| Cooperative Admin | `admin@karmsetu.in` | `Password123!` |
| Worker | `worker@karmsetu.in` | `Password123!` |
| Customer | `customer@karmsetu.in` | `Password123!` |
| Supervisor | `supervisor@karmsetu.in` | `Password123!` |

## Demo flow

The way we usually walk someone through this:

1. Log in as a **customer**, book a household service, and see the upfront estimate and a verified worker get suggested.
2. Switch to the **allocation view** and show the actual scoring breakdown behind that suggestion — skill match, distance, workload, reliability.
3. Log in as the assigned **worker**, accept the job, mark it complete.
4. Show the **settlement** that gets generated automatically — the 80/15/5 split, immediately visible.
5. Switch to the **cooperative admin** dashboard — updated roster utilization, active jobs, revenue ledger.
6. Show the **institutional view** with a multi-worker municipal contract, to make the point that this isn't just a household-booking app.
7. Close on the **analytics/forecast** page — this is the part that makes KarmSetu more than a scheduling tool.

## Future scope

What's in this repo is scoped to what's realistically buildable and demoable by a student team in a hackathon timeframe. Beyond that, the honest next steps we see are:

- A forecasting model that's actually trained on real booking data, once a cooperative has generated enough of it — right now it's intentionally a transparent statistical model, not ML, because we don't have the data to responsibly claim otherwise
- Real integration with e-Shram / PM-SYM / PMSBY instead of reminder tracking, if those portals expose anything integrable
- Supporting more than one cooperative talking to each other — a shared, opt-in worker pool across a federation of cooperatives for very large contracts
- Actual UPI/payment gateway integration instead of settlement simulation
- Supervisor mobile app for on-site job verification instead of a web view

## Team & contributions

Built by [Team Name] for SIH 2026.

| Name | Focus area |
|---|---|
| — | Backend / allocation & forecasting engines |
| — | Frontend / UI |
| — | Research & documentation |

If you're reviewing this for SIH judging and want to dig into a specific engine's logic, the allocation scoring lives in `backend/app/services/allocation_engine.py` and is unit-tested in `backend/tests/test_allocation.py` — that's the fastest way to see the actual math rather than take our word for it.

---

*Every factual claim about cooperatives, the unorganised workforce, or existing platforms made in this README and in our pitch deck is sourced in `docs/RESEARCH.md`, with links to the original government replies, reports, or papers. We'd rather cite three verified numbers than ten impressive-sounding ones.*
