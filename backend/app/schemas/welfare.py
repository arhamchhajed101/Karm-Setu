from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class WelfareRecordCreate(BaseModel):
    worker_id: int
    cooperative_id: int
    scheme_name: str
    policy_number: str
    status: str = "ACTIVE"
    coverage_amount: float = 200000.0
    annual_premium: float = 20.0
    start_date: date
    end_date: date
    contribution_status: str = "UP_TO_DATE"


class WelfareRecordResponse(BaseModel):
    id: int
    worker_id: int
    worker_name: Optional[str] = None
    cooperative_id: int
    cooperative_name: Optional[str] = None
    scheme_name: str
    policy_number: str
    status: str
    coverage_amount: float
    annual_premium: float
    start_date: date
    end_date: date
    contribution_status: str
    last_contribution_date: Optional[date]
    total_welfare_contributed: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WelfareAlert(BaseModel):
    worker_id: int
    worker_name: str
    scheme_name: str
    policy_number: str
    alert_type: str  # EXPIRING_SOON, EXPIRED, CONTRIBUTION_OVERDUE, UNENROLLED
    message: str
    days_remaining: Optional[int] = None


class WorkerWelfareProfileResponse(BaseModel):
    worker_id: int
    worker_name: str
    welfare_status: str
    welfare_balance: float
    active_schemes_count: int
    records: List[WelfareRecordResponse]
    alerts: List[WelfareAlert]
