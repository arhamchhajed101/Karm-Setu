from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict


class CustomerBase(BaseModel):
    name: str
    phone: str
    email: EmailStr
    address: Optional[str] = None
    city: str = "Delhi"
    latitude: float = 28.6139
    longitude: float = 77.2090


class CustomerCreate(CustomerBase):
    user_id: Optional[int] = None


class CustomerResponse(CustomerBase):
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
