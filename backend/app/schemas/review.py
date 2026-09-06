from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class ReviewCreate(BaseModel):
    job_id: int
    rating: float = Field(..., ge=1.0, le=5.0)
    comment: Optional[str] = None
    tags: List[str] = []


class ReviewResponse(BaseModel):
    id: int
    job_id: int
    customer_id: int
    customer_name: Optional[str] = None
    worker_id: int
    worker_name: Optional[str] = None
    rating: float
    comment: Optional[str]
    tags: List[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
