import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_role
from app.models.user import User, UserRole
from app.models.job import Job, JobStatus, PaymentStatus
from app.models.service import Service
from app.models.customer import Customer
from app.models.worker import Worker
from app.models.cooperative import Cooperative
from app.schemas.job import (
    JobCreate,
    JobResponse,
    JobEstimateRequest,
    JobEstimateResponse,
    JobStatusUpdate,
)
from app.services.audit_service import AuditService
from app.services.settlement_engine import SettlementEngine

router = APIRouter()


def _format_job(j: Job) -> JobResponse:
    return JobResponse(
        id=j.id,
        booking_ref=j.booking_ref,
        customer_id=j.customer_id,
        customer_name=j.customer.name if j.customer else None,
        customer_phone=j.customer.phone if j.customer else None,
        service_id=j.service_id,
        service_name=j.service.name if j.service else None,
        service_category=j.service.category if j.service else None,
        cooperative_id=j.cooperative_id,
        cooperative_name=j.cooperative.name if j.cooperative else None,
        assigned_worker_id=j.assigned_worker_id,
        assigned_worker_name=j.assigned_worker.name if j.assigned_worker else None,
        assigned_worker_phone=j.assigned_worker.phone if j.assigned_worker else None,
        status=j.status,
        slot_start=j.slot_start,
        slot_end=j.slot_end,
        address=j.address,
        latitude=j.latitude,
        longitude=j.longitude,
        is_emergency=j.is_emergency,
        price_estimate=j.price_estimate,
        final_price=j.final_price,
        payment_status=j.payment_status,
        payment_method=j.payment_method,
        customer_notes=j.customer_notes,
        worker_notes=j.worker_notes,
        cancellation_reason=j.cancellation_reason,
        supervisor_verified=j.supervisor_verified or False,
        created_at=j.created_at,
        started_at=j.started_at,
        completed_at=j.completed_at,
    )


@router.post("/estimate", response_model=JobEstimateResponse)
def get_job_estimate(req: JobEstimateRequest, db: Session = Depends(get_db)):
    """
    Computes a transparent upfront cost estimate including base fee, travel fee, and emergency multiplier.
    """
    service = db.query(Service).filter(Service.id == req.service_id).first()
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")

    base = service.base_price
    # Standard travel allowance (₹50 base travel fee)
    travel_fee = 50.0
    emergency_surge = round(base * (service.emergency_multiplier - 1.0), 2) if req.is_emergency else 0.0
    estimated_total = round(base + travel_fee + emergency_surge, 2)

    return JobEstimateResponse(
        service_id=service.id,
        service_name=service.name,
        base_price=base,
        travel_fee=travel_fee,
        emergency_surge=emergency_surge,
        estimated_total=estimated_total,
        estimated_duration_minutes=service.estimated_duration_minutes,
        serving_cooperative_id=service.cooperative_id,
        serving_cooperative_name=service.cooperative.name if service.cooperative else "Cooperative",
    )


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    job_in: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Creates a new service booking request from a customer.
    """
    service = db.query(Service).filter(Service.id == job_in.service_id).first()
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")

    customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()
    if not customer:
        customer = Customer(
            user_id=current_user.id,
            name=current_user.full_name,
            phone=current_user.phone or "",
            email=current_user.email,
            address=job_in.address,
            city="Delhi",
            latitude=job_in.latitude,
            longitude=job_in.longitude,
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)

    # Calculate price estimate
    base = service.base_price
    travel_fee = 50.0
    emergency_surge = round(base * (service.emergency_multiplier - 1.0), 2) if job_in.is_emergency else 0.0
    price_est = round(base + travel_fee + emergency_surge, 2)

    booking_ref = f"KS-{datetime.now().year}-{uuid.uuid4().hex[:6].upper()}"

    job = Job(
        booking_ref=booking_ref,
        customer_id=customer.id,
        service_id=service.id,
        cooperative_id=service.cooperative_id,
        status=JobStatus.REQUESTED,
        slot_start=job_in.slot_start,
        slot_end=job_in.slot_end,
        address=job_in.address,
        latitude=job_in.latitude,
        longitude=job_in.longitude,
        is_emergency=job_in.is_emergency,
        price_estimate=price_est,
        payment_status=PaymentStatus.PENDING,
        payment_method=job_in.payment_method,
        customer_notes=job_in.customer_notes,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    AuditService.log_event(
        db,
        entity_type="JOB",
        entity_id=job.id,
        action="REQUESTED",
        actor_id=current_user.id,
        actor_role=current_user.role.value,
        details={"booking_ref": booking_ref, "service": service.name, "estimate": price_est}
    )

    return _format_job(job)


@router.get("", response_model=List[JobResponse])
def list_jobs(
    status: Optional[JobStatus] = None,
    cooperative_id: Optional[int] = None,
    worker_id: Optional[int] = None,
    customer_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lists jobs with filters based on status, cooperative, worker, or customer.
    """
    query = db.query(Job)
    if status:
        query = query.filter(Job.status == status)
    if cooperative_id:
        query = query.filter(Job.cooperative_id == cooperative_id)
    if worker_id:
        query = query.filter(Job.assigned_worker_id == worker_id)
    if customer_id:
        query = query.filter(Job.customer_id == customer_id)

    # If current user is worker, restrict to their jobs
    if current_user.role == UserRole.WORKER and current_user.worker_profile:
        query = query.filter(Job.assigned_worker_id == current_user.worker_profile.id)

    jobs = query.order_by(Job.created_at.desc()).offset(skip).limit(limit).all()
    return [_format_job(j) for j in jobs]


@router.get("/{id}", response_model=JobResponse)
def get_job(id: int, db: Session = Depends(get_db)):
    """
    Retrieves job details and status tracking timeline.
    """
    job = db.query(Job).filter(Job.id == id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return _format_job(job)


@router.patch("/{id}/status", response_model=JobResponse)
def update_job_status(
    id: int,
    status_in: JobStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Transitions the job through its lifecycle state machine:
    REQUESTED -> ASSIGNED -> ACCEPTED -> IN_PROGRESS -> COMPLETED -> CANCELLED.
    Triggers automated settlement and fund allocation upon completion.
    """
    job = db.query(Job).filter(Job.id == id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    old_status = job.status
    job.status = status_in.status

    if status_in.notes:
        job.worker_notes = status_in.notes
    if status_in.cancellation_reason:
        job.cancellation_reason = status_in.cancellation_reason
    if status_in.final_price is not None:
        job.final_price = status_in.final_price

    now = datetime.now(timezone.utc)
    if status_in.status == JobStatus.ACCEPTED and not job.accepted_at:
        job.accepted_at = now
    elif status_in.status == JobStatus.IN_PROGRESS and not job.started_at:
        job.started_at = now
    elif status_in.status == JobStatus.COMPLETED:
        job.completed_at = now
        if not job.final_price:
            job.final_price = job.price_estimate
        # If job is completed, execute cooperative settlement calculation
        if job.assigned_worker_id:
            SettlementEngine.process_job_settlement(
                db=db,
                job=job,
                payment_method=job.payment_method,
                notes=f"Settlement upon status COMPLETED for {job.booking_ref}"
            )

    db.commit()
    db.refresh(job)

    AuditService.log_event(
        db,
        entity_type="JOB",
        entity_id=job.id,
        action=f"STATUS_CHANGE_{status_in.status.value}",
        actor_id=current_user.id,
        actor_role=current_user.role.value,
        details={"from": old_status.value, "to": status_in.status.value, "notes": status_in.notes}
    )

    return _format_job(job)


@router.post("/{id}/supervisor-verify", response_model=JobResponse)
def supervisor_verify_job(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.SUPERVISOR, UserRole.COOPERATIVE_ADMIN))
):
    """
    Enables official supervisor inspection and sign-off for institutional/quality-controlled jobs (PRD P1).
    """
    job = db.query(Job).filter(Job.id == id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    job.supervisor_verified = True
    job.supervisor_id = current_user.id
    db.commit()
    db.refresh(job)

    AuditService.log_event(
        db,
        entity_type="JOB",
        entity_id=job.id,
        action="SUPERVISOR_VERIFIED",
        actor_id=current_user.id,
        actor_role=current_user.role.value,
        details={"supervisor_name": current_user.full_name}
    )

    return _format_job(job)
