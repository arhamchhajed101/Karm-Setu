from datetime import date, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_role
from app.models.user import User, UserRole
from app.models.worker import Worker
from app.models.cooperative import Cooperative
from app.models.welfare import WelfareRecord
from app.schemas.welfare import (
    WelfareRecordCreate,
    WelfareRecordResponse,
    WelfareAlert,
    WorkerWelfareProfileResponse,
)

router = APIRouter()


def _format_welfare(r: WelfareRecord) -> WelfareRecordResponse:
    return WelfareRecordResponse(
        id=r.id,
        worker_id=r.worker_id,
        worker_name=r.worker.name if r.worker else None,
        cooperative_id=r.cooperative_id,
        cooperative_name=r.cooperative.name if r.cooperative else None,
        scheme_name=r.scheme_name,
        policy_number=r.policy_number,
        status=r.status,
        coverage_amount=r.coverage_amount,
        annual_premium=r.annual_premium,
        start_date=r.start_date,
        end_date=r.end_date,
        contribution_status=r.contribution_status,
        last_contribution_date=r.last_contribution_date,
        total_welfare_contributed=r.total_welfare_contributed,
        created_at=r.created_at,
    )


@router.get("/worker/{worker_id}", response_model=WorkerWelfareProfileResponse)
def get_worker_welfare_profile(worker_id: int, db: Session = Depends(get_db)):
    """
    Retrieves full social security & insurance portfolio for a worker (e-Shram PM-SYM, PMSBY, State Welfare Board).
    Generates dynamic alerts for policies nearing expiration or requiring renewal contributions.
    """
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Worker not found")

    records = db.query(WelfareRecord).filter(WelfareRecord.worker_id == worker_id).all()
    today = date.today()
    alerts: List[WelfareAlert] = []

    for r in records:
        days_left = (r.end_date - today).days
        if days_left < 0:
            alerts.append(
                WelfareAlert(
                    worker_id=worker.id,
                    worker_name=worker.name,
                    scheme_name=r.scheme_name,
                    policy_number=r.policy_number,
                    alert_type="EXPIRED",
                    message=f"Insurance policy {r.scheme_name} expired {abs(days_left)} days ago. Renewal required.",
                    days_remaining=days_left,
                )
            )
        elif days_left <= 30:
            alerts.append(
                WelfareAlert(
                    worker_id=worker.id,
                    worker_name=worker.name,
                    scheme_name=r.scheme_name,
                    policy_number=r.policy_number,
                    alert_type="EXPIRING_SOON",
                    message=f"{r.scheme_name} coverage expires in {days_left} days. Cooperative welfare pool contribution will be auto-applied.",
                    days_remaining=days_left,
                )
            )

    return WorkerWelfareProfileResponse(
        worker_id=worker.id,
        worker_name=worker.name,
        welfare_status=worker.welfare_status,
        welfare_balance=worker.welfare_balance or 0.0,
        active_schemes_count=len([r for r in records if r.status == "ACTIVE"]),
        records=[_format_welfare(r) for r in records],
        alerts=alerts,
    )


@router.post("/records", response_model=WelfareRecordResponse, status_code=status.HTTP_201_CREATED)
def create_welfare_record(
    record_in: WelfareRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.COOPERATIVE_ADMIN, UserRole.SUPERVISOR))
):
    """
    Enrolls a cooperative worker into a social security or insurance policy.
    """
    worker = db.query(Worker).filter(Worker.id == record_in.worker_id).first()
    if not worker:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Worker not found")

    existing = db.query(WelfareRecord).filter(WelfareRecord.policy_number == record_in.policy_number).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Policy number already registered.")

    record = WelfareRecord(
        worker_id=record_in.worker_id,
        cooperative_id=record_in.cooperative_id,
        scheme_name=record_in.scheme_name,
        policy_number=record_in.policy_number,
        status=record_in.status,
        coverage_amount=record_in.coverage_amount,
        annual_premium=record_in.annual_premium,
        start_date=record_in.start_date,
        end_date=record_in.end_date,
        contribution_status=record_in.contribution_status,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return _format_welfare(record)


@router.get("/alerts", response_model=List[WelfareAlert])
def list_welfare_alerts(
    cooperative_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """
    Lists system-wide welfare and insurance alerts for cooperative administrators.
    """
    today = date.today()
    query = db.query(WelfareRecord)
    if cooperative_id:
        query = query.filter(WelfareRecord.cooperative_id == cooperative_id)

    records = query.all()
    alerts: List[WelfareAlert] = []

    for r in records:
        days_left = (r.end_date - today).days
        if days_left <= 30:
            w_name = r.worker.name if r.worker else f"Worker #{r.worker_id}"
            alert_type = "EXPIRED" if days_left < 0 else "EXPIRING_SOON"
            msg = (
                f"{r.scheme_name} for {w_name} has expired."
                if days_left < 0
                else f"{r.scheme_name} for {w_name} expires in {days_left} days."
            )
            alerts.append(
                WelfareAlert(
                    worker_id=r.worker_id,
                    worker_name=w_name,
                    scheme_name=r.scheme_name,
                    policy_number=r.policy_number,
                    alert_type=alert_type,
                    message=msg,
                    days_remaining=days_left,
                )
            )
    return alerts
