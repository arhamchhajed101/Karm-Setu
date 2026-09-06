from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class InstitutionalProjectCreate(BaseModel):
    client_name: str
    title: str
    description: Optional[str] = None
    cooperative_id: int
    supervisor_id: Optional[int] = None
    required_headcount: int
    skills_breakdown: dict  # {"Plumber": 3, "Electrician": 2}
    start_date: date
    end_date: date
    budget: float
    milestones: List[dict] = []


class InstitutionalProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    supervisor_id: Optional[int] = None
    required_headcount: Optional[int] = None
    skills_breakdown: Optional[dict] = None
    assigned_workers: Optional[List[int]] = None
    status: Optional[str] = None
    progress_percentage: Optional[float] = None
    milestones: Optional[List[dict]] = None
    amount_disbursed: Optional[float] = None


class InstitutionalProjectResponse(BaseModel):
    id: int
    client_name: str
    title: str
    description: Optional[str]
    cooperative_id: int
    cooperative_name: Optional[str] = None
    supervisor_id: Optional[int]
    supervisor_name: Optional[str] = None
    required_headcount: int
    skills_breakdown: dict
    assigned_workers: List[int]
    start_date: date
    end_date: date
    budget: float
    amount_disbursed: float
    status: str
    progress_percentage: float
    milestones: List[dict]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
