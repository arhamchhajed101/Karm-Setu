from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class ServiceBase(BaseModel):
    cooperative_id: int
    category: str
    name: str
    description: Optional[str] = None
    pricing_model: str = "FIXED"  # FIXED, INSPECTION_DIAGNOSTIC, HOURLY
    base_price: float
    estimated_duration_minutes: int = 60
    emergency_multiplier: float = 1.25
    required_skills: List[str] = []
    is_active: bool = True


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    category: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    pricing_model: Optional[str] = None
    base_price: Optional[float] = None
    estimated_duration_minutes: Optional[int] = None
    emergency_multiplier: Optional[float] = None
    required_skills: Optional[List[str]] = None
    is_active: Optional[bool] = None


class ServiceResponse(ServiceBase):
    id: int
    cooperative_name: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
