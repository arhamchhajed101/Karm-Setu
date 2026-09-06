from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.job import JobStatus, PaymentStatus


class JobCreate(BaseModel):
    service_id: int
    slot_start: datetime
    slot_end: datetime
    address: str
    latitude: float
    longitude: float
    is_emergency: bool = False
    customer_notes: Optional[str] = None
    payment_method: str = "ONLINE_SIMULATED"  # ONLINE_SIMULATED, CASH_ON_DELIVERY, DIRECT_UPI


class JobEstimateRequest(BaseModel):
    service_id: int
    latitude: float
    longitude: float
    is_emergency: bool = False


class JobEstimateResponse(BaseModel):
    service_id: int
    service_name: str
    base_price: float
    travel_fee: float
    emergency_surge: float
    estimated_total: float
    estimated_duration_minutes: int
    serving_cooperative_id: int
    serving_cooperative_name: str


class JobStatusUpdate(BaseModel):
    status: JobStatus
    notes: Optional[str] = None
    cancellation_reason: Optional[str] = None
    final_price: Optional[float] = None


class JobResponse(BaseModel):
    id: int
    booking_ref: str
    customer_id: int
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    service_id: int
    service_name: Optional[str] = None
    service_category: Optional[str] = None
    cooperative_id: int
    cooperative_name: Optional[str] = None
    assigned_worker_id: Optional[int] = None
    assigned_worker_name: Optional[str] = None
    assigned_worker_phone: Optional[str] = None
    status: JobStatus
    slot_start: datetime
    slot_end: datetime
    address: str
    latitude: float
    longitude: float
    is_emergency: bool
    price_estimate: float
    final_price: Optional[float]
    payment_status: PaymentStatus
    payment_method: str
    customer_notes: Optional[str]
    worker_notes: Optional[str]
    cancellation_reason: Optional[str]
    supervisor_verified: bool
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)
