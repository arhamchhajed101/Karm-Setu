from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.api.v1.api_router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Creates database tables automatically on startup if they do not exist."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="KarmSetu API - Cooperative-Owned Digital Service Marketplace",
    description="""
# KarmSetu — SIH 2026 Core Platform
A cooperative-owned digital operating platform that connects service demand with verified cooperative workers 
and provides workforce intelligence, explainable smart allocation, demand forecasting, and worker welfare management.

### Key Capabilities:
* **Explainable Fair Allocation**: 6-dimension weighted scoring engine (Skill, Availability, Distance, Reliability, Workload, Fairness equalization) with explainability narratives.
* **Cooperative Operating System**: Workforce roster, live availability, KPIs, and service catalogue.
* **Financial Ledger & Settlement**: Automated revenue split (Worker ~80%, Cooperative ~15%, Welfare Pool ~5%) and COD/Online payment simulation.
* **Worker Welfare & Social Security**: e-Shram PM-SYM, PMSBY, PMJJBY insurance tracking with proactive renewal alerts.
* **Demand Forecasting & Skill Gaps**: Time-series predictive analytics with seasonal indices, confidence intervals, and capacity alerts.
* **Institutional Multi-Worker Projects**: Enterprise contract management and supervisor inspection verification.
    """,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["System"])
def health_check():
    """System health check and readiness probe."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": settings.DATABASE_URL.split("://")[0],
    }


@app.get("/", tags=["System"])
def root():
    """Welcome endpoint with links to interactive documentation."""
    return {
        "message": "Welcome to KarmSetu API - Cooperative-Owned Digital Service Marketplace",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "api_v1": settings.API_V1_STR,
    }
