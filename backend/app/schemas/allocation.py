from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class ScoreBreakdown(BaseModel):
    skill_score: float         # 0-30 max
    availability_score: float  # 0-20 max
    distance_score: float      # 0-15 max
    reliability_score: float   # 0-15 max
    workload_score: float      # 0-10 max
    fairness_score: float      # 0-10 max
    total_score: float         # 0-100 max


class AllocationCandidate(BaseModel):
    worker_id: int
    worker_name: str
    worker_phone: str
    photo_url: Optional[str] = None
    rating: float
    verification_status: str
    distance_km: float
    weekly_jobs: int
    scores: ScoreBreakdown
    narrative_explanation: str


class AllocationEvaluateResponse(BaseModel):
    job_id: int
    booking_ref: str
    service_name: str
    service_category: str
    job_location: dict
    candidates: List[AllocationCandidate]
    recommended_worker_id: Optional[int] = None
    recommended_worker_name: Optional[str] = None
    top_recommendation_reason: Optional[str] = None
    total_eligible_workers: int
    evaluated_at: datetime


class ManualAssignRequest(BaseModel):
    worker_id: int
    coordinator_notes: Optional[str] = None


class AutoAssignResponse(BaseModel):
    job_id: int
    booking_ref: str
    assigned_worker_id: int
    assigned_worker_name: str
    assigned_worker_phone: str
    total_score: float
    narrative_explanation: str
    status: str
