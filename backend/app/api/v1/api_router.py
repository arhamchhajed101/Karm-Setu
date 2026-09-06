from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    cooperatives,
    workers,
    services,
    customers,
    jobs,
    allocation,
    settlements,
    welfare,
    analytics,
    institutional,
    reviews,
    audit,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication & Profiles"])
api_router.include_router(cooperatives.router, prefix="/cooperatives", tags=["Cooperatives & Rosters"])
api_router.include_router(workers.router, prefix="/workers", tags=["Workers & Availability"])
api_router.include_router(services.router, prefix="/services", tags=["Services Catalogue"])
api_router.include_router(customers.router, prefix="/customers", tags=["Customers"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["Jobs Lifecycle & Estimates"])
api_router.include_router(allocation.router, prefix="/allocation", tags=["Smart Fair Allocation & Explainability"])
api_router.include_router(settlements.router, prefix="/settlements", tags=["Cooperative Settlements & Ledger"])
api_router.include_router(welfare.router, prefix="/welfare", tags=["Worker Welfare & e-Shram Insurance"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Demand Forecasting & Workforce Analytics"])
api_router.include_router(institutional.router, prefix="/institutional", tags=["Institutional Multi-Worker Projects"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["Reviews & Trust Records"])
api_router.include_router(audit.router, prefix="/audit", tags=["Compliance & Audit Trails"])
