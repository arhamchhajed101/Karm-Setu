from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.worker import Worker
from app.models.job import Job, JobStatus
from app.schemas.analytics import (
    CategoryForecastResponse,
    DemandHeatmapPoint,
    SkillGapAlert,
    WorkerUtilizationMetrics,
)
from app.services.forecasting_engine import DemandForecastingEngine

router = APIRouter()


@router.get("/forecast", response_model=CategoryForecastResponse)
def get_demand_forecast(
    zone: str = Query("Central Delhi", description="Geographic zone/district"),
    category: str = Query("Plumbing", description="Service trade category"),
    days_ahead: int = Query(7, ge=1, le=30, description="Forecast horizon in days"),
    db: Session = Depends(get_db),
):
    """
    Computes time-series demand forecasting with seasonal adjustments, confidence intervals, and capacity recommendations.
    """
    return DemandForecastingEngine.get_forecast_for_category(
        db=db, zone=zone, category=category, days_ahead=days_ahead
    )


@router.get("/skill-gaps", response_model=List[SkillGapAlert])
def get_skill_gaps(
    zone: str = Query("Central Delhi", description="Geographic zone"),
    db: Session = Depends(get_db),
):
    """
    Identifies trade deficits where upcoming projected peak demand exceeds verified cooperative roster supply.
    """
    return DemandForecastingEngine.detect_skill_gaps(db=db, zone=zone)


@router.get("/heatmap", response_model=List[DemandHeatmapPoint])
def get_demand_heatmap(db: Session = Depends(get_db)):
    """
    Provides geospatial booking density heatmap coordinates for interactive map rendering.
    """
    return DemandForecastingEngine.get_demand_heatmap(db=db)


@router.get("/utilization/{cooperative_id}", response_model=WorkerUtilizationMetrics)
def get_cooperative_utilization_metrics(
    cooperative_id: int, db: Session = Depends(get_db)
):
    """
    Calculates fairness distribution metrics and workload concentration across the cooperative.
    Computes Gini coefficient of job distribution to evaluate fairness improvements.
    """
    workers = db.query(Worker).filter(Worker.cooperative_id == cooperative_id).all()
    if not workers:
        return WorkerUtilizationMetrics(
            cooperative_id=cooperative_id,
            average_utilization_rate=0.0,
            fairness_gini_coefficient=0.0,
            overworked_workers_count=0,
            underutilized_workers_count=0,
            optimal_workers_count=0,
        )

    workloads = [w.weekly_jobs_count or 0 for w in workers]
    total_workers = len(workers)
    avg_util = sum(workloads) / total_workers if total_workers > 0 else 0.0

    overworked = sum(1 for w in workloads if w > 8)
    underutilized = sum(1 for w in workloads if w < 2)
    optimal = total_workers - overworked - underutilized

    # Calculate Gini coefficient for fair distribution
    sorted_loads = sorted(workloads)
    total_load = sum(sorted_loads)
    if total_load == 0:
        gini = 0.0
    else:
        n = total_workers
        cumulative = sum((i + 1) * load for i, load in enumerate(sorted_loads))
        gini = round((2 * cumulative) / (n * total_load) - (n + 1) / n, 3)
        gini = max(0.0, min(1.0, gini))

    return WorkerUtilizationMetrics(
        cooperative_id=cooperative_id,
        average_utilization_rate=round(avg_util, 2),
        fairness_gini_coefficient=gini,
        overworked_workers_count=overworked,
        underutilized_workers_count=underutilized,
        optimal_workers_count=optimal,
    )
