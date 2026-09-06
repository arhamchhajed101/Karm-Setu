from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, ConfigDict


class WorkerBase(BaseModel):
    name: str
    phone: str
    cooperative_id: int
    photo_url: Optional[str] = None
    skills: List[str] = []
    experience_years: int = 1
    certificates: List[dict] = []
    verification_status: str = "VERIFIED"
    verification_ref_id: Optional[str] = None
    police_station_jurisdiction: Optional[str] = None
    availability_status: str = "AVAILABLE"  # AVAILABLE, BUSY, OFF_DUTY
    latitude: float = 28.6139
    longitude: float = 77.2090
    address: Optional[str] = None


class WorkerCreate(WorkerBase):
    user_id: Optional[int] = None


class WorkerUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    photo_url: Optional[str] = None
    skills: Optional[List[str]] = None
    experience_years: Optional[int] = None
    certificates: Optional[List[dict]] = None
    verification_status: Optional[str] = None
    verification_ref_id: Optional[str] = None
    police_station_jurisdiction: Optional[str] = None
    availability_status: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None


class AvailabilityUpdate(BaseModel):
    availability_status: str  # AVAILABLE, BUSY, OFF_DUTY


class WorkerResponse(BaseModel):
    id: int
    user_id: int
    cooperative_id: int
    cooperative_name: Optional[str] = None
    name: str
    phone: str
    photo_url: Optional[str]
    skills: List[str]
    experience_years: int
    certificates: List[dict]
    verification_status: str
    verification_ref_id: Optional[str]
    police_station_jurisdiction: Optional[str]
    rating: float
    total_jobs: int
    weekly_jobs_count: int
    reliability_score: float
    availability_status: str
    latitude: float
    longitude: float
    address: Optional[str]
    welfare_status: str
    total_earnings: float
    welfare_balance: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkerRosterItem(BaseModel):
    id: int
    name: str
    phone: str
    skills: List[str]
    verification_status: str
    rating: float
    total_jobs: int
    weekly_jobs_count: int
    availability_status: str
    welfare_status: str
    latitude: float
    longitude: float
