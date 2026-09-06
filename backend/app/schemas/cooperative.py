from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class CooperativeBase(BaseModel):
    name: str
    registration_id: str
    state: str
    district: str
    address: Optional[str] = None
    pin_code: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    type: str = "Labour Contract Society"
    verification_status: str = "VERIFIED"
    service_categories: List[str] = []
    commission_rate: float = 0.15
    welfare_contribution_rate: float = 0.05


class CooperativeCreate(CooperativeBase):
    pass


class CooperativeUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    service_categories: Optional[List[str]] = None
    commission_rate: Optional[float] = None
    welfare_contribution_rate: Optional[float] = None
    verification_status: Optional[str] = None


class CooperativeResponse(BaseModel):
    id: int
    name: str
    registration_id: str
    state: str
    district: str
    address: Optional[str]
    pin_code: Optional[str]
    contact_phone: Optional[str]
    contact_email: Optional[str]
    type: str
    verification_status: str
    service_categories: List[str]
    commission_rate: float
    welfare_contribution_rate: float
    total_members: int
    total_jobs_completed: int
    welfare_fund_pool: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CooperativeKPIs(BaseModel):
    cooperative_id: int
    name: str
    total_workers: int
    active_available_workers: int
    busy_workers: int
    total_jobs_completed: int
    active_jobs_count: int
    total_revenue: float
    total_welfare_pool: float
    average_worker_rating: float
    top_categories: List[dict]
