from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class SettlementResponse(BaseModel):
    id: int
    job_id: int
    booking_ref: Optional[str] = None
    cooperative_id: int
    cooperative_name: Optional[str] = None
    worker_id: int
    worker_name: Optional[str] = None
    gross_amount: float
    worker_amount: float
    cooperative_amount: float
    welfare_amount: float
    adjustment_amount: float
    payment_method: str
    payment_status: str
    settlement_status: str
    notes: Optional[str] = None
    settled_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SettlementSummaryResponse(BaseModel):
    cooperative_id: int
    total_gross_settled: float
    total_worker_disbursed: float
    total_cooperative_retained: float
    total_welfare_fund_contributed: float
    total_transactions_count: int
    pending_settlements_count: int


class PaymentSimulationRequest(BaseModel):
    job_id: int
    payment_method: str = "ONLINE_SIMULATED"  # ONLINE_SIMULATED, CASH_ON_DELIVERY, DIRECT_UPI
    amount: float
    simulate_status: str = "PAID"  # PAID, REFUNDED, FAILED
