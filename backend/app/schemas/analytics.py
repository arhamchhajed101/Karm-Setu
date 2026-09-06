from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class DemandObservationResponse(BaseModel):
    id: int
    date: date
    zone: str
    service_category: str
    bookings_count: int
    completed_count: int
    cancellations_count: int
    avg_price: float
    lead_time_hours: float

    model_config = ConfigDict(from_attributes=True)


class ForecastPoint(BaseModel):
    date: str
    predicted_demand: float
    confidence_low: float
    confidence_high: float
    seasonal_factor: float


class CategoryForecastResponse(BaseModel):
    zone: str
    service_category: str
    current_active_workers: int
    daily_forecast: List[ForecastPoint]
    total_projected_demand_7d: float
    capacity_status: str  # DEFICIT, BALANCED, SURPLUS
    projected_utilization_pct: float
    recommendation: str


class DemandHeatmapPoint(BaseModel):
    zone: str
    latitude: float
    longitude: float
    total_bookings: int
    intensity: float  # 0.0 to 1.0


class SkillGapAlert(BaseModel):
    zone: str
    service_category: str
    required_skills: List[str]
    current_worker_count: int
    projected_peak_demand: float
    deficit_count: int
    severity: str  # HIGH, MEDIUM, LOW
    action_item: str


class WorkerUtilizationMetrics(BaseModel):
    cooperative_id: int
    average_utilization_rate: float
    fairness_gini_coefficient: float  # measure of equality in job distribution (0.0 = perfect equality)
    overworked_workers_count: int     # > 8 jobs/week
    underutilized_workers_count: int  # < 2 jobs/week
    optimal_workers_count: int
