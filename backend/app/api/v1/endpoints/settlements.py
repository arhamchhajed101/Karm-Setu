from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.deps import get_db, get_current_user, require_role
from app.models.user import User, UserRole
from app.models.job import Job, JobStatus, PaymentStatus
from app.models.cooperative import Cooperative
from app.models.settlement import CooperativeSettlement
from app.schemas.settlement import (
    SettlementResponse,
    SettlementSummaryResponse,
    PaymentSimulationRequest,
)
from app.services.settlement_engine import SettlementEngine
from app.services.audit_service import AuditService

router = APIRouter()


def _format_settlement(s: CooperativeSettlement) -> SettlementResponse:
    return SettlementResponse(
        id=s.id,
        job_id=s.job_id,
        booking_ref=s.job.booking_ref if s.job else None,
        cooperative_id=s.cooperative_id,
        cooperative_name=s.cooperative.name if s.cooperative else None,
        worker_id=s.worker_id,
        worker_name=s.worker.name if s.worker else None,
        gross_amount=s.gross_amount,
        worker_amount=s.worker_amount,
        cooperative_amount=s.cooperative_amount,
        welfare_amount=s.welfare_amount,
        adjustment_amount=s.adjustment_amount,
        payment_method=s.payment_method,
        payment_status=s.payment_status,
        settlement_status=s.settlement_status,
        notes=s.notes,
        settled_at=s.settled_at,
    )


@router.get("", response_model=List[SettlementResponse])
def list_settlements(
    cooperative_id: Optional[int] = None,
    worker_id: Optional[int] = None,
    payment_status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lists transaction settlements and revenue distributions across cooperatives and workers.
    """
    query = db.query(CooperativeSettlement)
    if cooperative_id:
        query = query.filter(CooperativeSettlement.cooperative_id == cooperative_id)
    if worker_id:
        query = query.filter(CooperativeSettlement.worker_id == worker_id)
    if payment_status:
        query = query.filter(CooperativeSettlement.payment_status == payment_status)

    settlements = query.order_by(CooperativeSettlement.settled_at.desc()).offset(skip).limit(limit).all()
    return [_format_settlement(s) for s in settlements]


@router.get("/{id}", response_model=SettlementResponse)
def get_settlement(id: int, db: Session = Depends(get_db)):
    """
    Retrieves a single settlement record.
    """
    s = db.query(CooperativeSettlement).filter(CooperativeSettlement.id == id).first()
    if not s:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Settlement not found")
    return _format_settlement(s)


@router.post("/simulate-payment", response_model=SettlementResponse)
def simulate_customer_payment(
    req: PaymentSimulationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Simulates customer online payment or cash collection (PRD Section 3.3).
    Executes automated financial ledger distribution:
    - Worker earnings disbursed (~80%)
    - Cooperative operational commission retained (~15%)
    - Worker welfare & social security fund contributed (~5%)
    """
    job = db.query(Job).filter(Job.id == req.job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    job.final_price = req.amount
    job.payment_method = req.payment_method
    job.payment_status = PaymentStatus.PAID

    settlement = SettlementEngine.process_job_settlement(
        db=db,
        job=job,
        payment_method=req.payment_method,
        notes=f"Simulated {req.payment_method} payment of ₹{req.amount} verified by {current_user.full_name}"
    )

    AuditService.log_event(
        db,
        entity_type="PAYMENT",
        entity_id=job.id,
        action="PAYMENT_SIMULATED",
        actor_id=current_user.id,
        actor_role=current_user.role.value,
        details={
            "amount": req.amount,
            "method": req.payment_method,
            "worker_disbursed": settlement.worker_amount,
            "welfare_fund_pool_add": settlement.welfare_amount,
        }
    )

    return _format_settlement(settlement)


@router.get("/cooperative/{cooperative_id}/summary", response_model=SettlementSummaryResponse)
def get_cooperative_settlement_summary(
    cooperative_id: int, db: Session = Depends(get_db)
):
    """
    Returns aggregated settlement metrics for a cooperative's finance dashboard.
    """
    coop = db.query(Cooperative).filter(Cooperative.id == cooperative_id).first()
    if not coop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cooperative not found")

    totals = (
        db.query(
            func.sum(CooperativeSettlement.gross_amount).label("gross"),
            func.sum(CooperativeSettlement.worker_amount).label("worker"),
            func.sum(CooperativeSettlement.cooperative_amount).label("coop"),
            func.sum(CooperativeSettlement.welfare_amount).label("welfare"),
            func.count(CooperativeSettlement.id).label("count"),
        )
        .filter(CooperativeSettlement.cooperative_id == cooperative_id)
        .first()
    )

    pending = (
        db.query(Job)
        .filter(
            Job.cooperative_id == cooperative_id,
            Job.status == JobStatus.COMPLETED,
            Job.payment_status == PaymentStatus.PENDING,
        )
        .count()
    )

    return SettlementSummaryResponse(
        cooperative_id=cooperative_id,
        total_gross_settled=round(totals.gross or 0.0, 2),
        total_worker_disbursed=round(totals.worker or 0.0, 2),
        total_cooperative_retained=round(totals.coop or 0.0, 2),
        total_welfare_fund_contributed=round(totals.welfare or 0.0, 2),
        total_transactions_count=totals.count or 0,
        pending_settlements_count=pending,
    )
