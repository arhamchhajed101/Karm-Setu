import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_role
from app.models.user import User, UserRole
from app.models.worker import Worker
from app.models.cooperative import Cooperative
from app.models.job import Job, JobStatus
from app.models.settlement import CooperativeSettlement
from app.schemas.worker import (
    WorkerCreate,
    WorkerUpdate,
    WorkerResponse,
    AvailabilityUpdate,
)

router = APIRouter()


def _format_worker(w: Worker) -> WorkerResponse:
    try:
        skills = json.loads(w.skills) if isinstance(w.skills, str) else (w.skills or [])
    except Exception:
        skills = []
    try:
        certs = json.loads(w.certificates) if isinstance(w.certificates, str) else (w.certificates or [])
    except Exception:
        certs = []

    return WorkerResponse(
        id=w.id,
        user_id=w.user_id,
        cooperative_id=w.cooperative_id,
        cooperative_name=w.cooperative.name if w.cooperative else None,
        name=w.name,
        phone=w.phone,
        photo_url=w.photo_url,
        skills=skills,
        experience_years=w.experience_years or 1,
        certificates=certs,
        verification_status=w.verification_status,
        verification_ref_id=w.verification_ref_id,
        police_station_jurisdiction=w.police_station_jurisdiction,
        rating=w.rating,
        total_jobs=w.total_jobs or 0,
        weekly_jobs_count=w.weekly_jobs_count or 0,
        reliability_score=w.reliability_score,
        availability_status=w.availability_status,
        latitude=w.latitude,
        longitude=w.longitude,
        address=w.address,
        welfare_status=w.welfare_status,
        total_earnings=w.total_earnings or 0.0,
        welfare_balance=w.welfare_balance or 0.0,
        created_at=w.created_at,
    )


@router.get("", response_model=List[WorkerResponse])
def list_workers(
    cooperative_id: Optional[int] = None,
    skill: Optional[str] = None,
    availability: Optional[str] = None,
    verification: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    Lists workers with optional multi-criteria filters (cooperative, skill, availability status, verification).
    """
    query = db.query(Worker)
    if cooperative_id:
        query = query.filter(Worker.cooperative_id == cooperative_id)
    if availability:
        query = query.filter(Worker.availability_status == availability)
    if verification:
        query = query.filter(Worker.verification_status == verification)
    if skill:
        query = query.filter(Worker.skills.ilike(f"%{skill}%"))

    workers = query.offset(skip).limit(limit).all()
    return [_format_worker(w) for w in workers]


@router.get("/{id}", response_model=WorkerResponse)
def get_worker(id: int, db: Session = Depends(get_db)):
    """
    Retrieves full worker profile including verification credentials and performance metrics.
    """
    w = db.query(Worker).filter(Worker.id == id).first()
    if not w:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Worker not found")
    return _format_worker(w)


@router.post("", response_model=WorkerResponse, status_code=status.HTTP_201_CREATED)
def create_worker(
    worker_in: WorkerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.COOPERATIVE_ADMIN, UserRole.SUPERVISOR))
):
    """
    Onboards a verified worker to the cooperative roster.
    """
    coop = db.query(Cooperative).filter(Cooperative.id == worker_in.cooperative_id).first()
    if not coop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cooperative not found")

    user_id = worker_in.user_id
    if not user_id:
        # Create a worker user record if not provided
        from app.core.security import get_password_hash
        new_user = User(
            email=f"worker_{worker_in.phone[-4:]}@karmsetu.in",
            hashed_password=get_password_hash("WorkerPass123!"),
            full_name=worker_in.name,
            phone=worker_in.phone,
            role=UserRole.WORKER,
            is_active=True,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        user_id = new_user.id

    worker = Worker(
        user_id=user_id,
        cooperative_id=worker_in.cooperative_id,
        name=worker_in.name,
        phone=worker_in.phone,
        photo_url=worker_in.photo_url,
        skills=json.dumps(worker_in.skills),
        experience_years=worker_in.experience_years,
        certificates=json.dumps(worker_in.certificates),
        verification_status=worker_in.verification_status,
        verification_ref_id=worker_in.verification_ref_id,
        police_station_jurisdiction=worker_in.police_station_jurisdiction,
        availability_status=worker_in.availability_status,
        latitude=worker_in.latitude,
        longitude=worker_in.longitude,
        address=worker_in.address,
        rating=4.8,
        reliability_score=0.95,
        total_jobs=0,
        weekly_jobs_count=0,
        welfare_status="ACTIVE",
    )
    db.add(worker)
    
    # Increment cooperative member count
    coop.total_members = (coop.total_members or 0) + 1
    db.commit()
    db.refresh(worker)

    return _format_worker(worker)


@router.put("/{id}", response_model=WorkerResponse)
def update_worker(
    id: int,
    worker_in: WorkerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Updates worker details, trade certifications, or coordinates.
    """
    worker = db.query(Worker).filter(Worker.id == id).first()
    if not worker:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Worker not found")

    if worker_in.name is not None:
        worker.name = worker_in.name
    if worker_in.phone is not None:
        worker.phone = worker_in.phone
    if worker_in.photo_url is not None:
        worker.photo_url = worker_in.photo_url
    if worker_in.skills is not None:
        worker.skills = json.dumps(worker_in.skills)
    if worker_in.experience_years is not None:
        worker.experience_years = worker_in.experience_years
    if worker_in.certificates is not None:
        worker.certificates = json.dumps(worker_in.certificates)
    if worker_in.verification_status is not None:
        worker.verification_status = worker_in.verification_status
    if worker_in.verification_ref_id is not None:
        worker.verification_ref_id = worker_in.verification_ref_id
    if worker_in.police_station_jurisdiction is not None:
        worker.police_station_jurisdiction = worker_in.police_station_jurisdiction
    if worker_in.availability_status is not None:
        worker.availability_status = worker_in.availability_status
    if worker_in.latitude is not None:
        worker.latitude = worker_in.latitude
    if worker_in.longitude is not None:
        worker.longitude = worker_in.longitude
    if worker_in.address is not None:
        worker.address = worker_in.address

    db.commit()
    db.refresh(worker)
    return _format_worker(worker)


@router.patch("/{id}/availability", response_model=WorkerResponse)
def update_worker_availability(
    id: int,
    avail_in: AvailabilityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Toggles worker availability (AVAILABLE, BUSY, OFF_DUTY).
    """
    worker = db.query(Worker).filter(Worker.id == id).first()
    if not worker:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Worker not found")

    if avail_in.availability_status not in ["AVAILABLE", "BUSY", "OFF_DUTY"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid availability state")

    worker.availability_status = avail_in.availability_status
    db.commit()
    db.refresh(worker)
    return _format_worker(worker)


@router.get("/{id}/earnings")
def get_worker_earnings(id: int, db: Session = Depends(get_db)):
    """
    Retrieves itemized earnings, completed jobs, and welfare deductions for worker dashboard.
    """
    worker = db.query(Worker).filter(Worker.id == id).first()
    if not worker:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Worker not found")

    settlements = (
        db.query(CooperativeSettlement)
        .filter(CooperativeSettlement.worker_id == id)
        .order_by(CooperativeSettlement.settled_at.desc())
        .limit(20)
        .all()
    )

    items = []
    for s in settlements:
        items.append({
            "job_id": s.job_id,
            "booking_ref": s.job.booking_ref if s.job else None,
            "service_name": s.job.service.name if s.job and s.job.service else "Service",
            "gross_amount": s.gross_amount,
            "disbursed_to_worker": s.worker_amount,
            "welfare_fund_saved": s.welfare_amount,
            "date": s.settled_at,
        })

    return {
        "worker_id": worker.id,
        "name": worker.name,
        "total_earnings": worker.total_earnings or 0.0,
        "welfare_balance": worker.welfare_balance or 0.0,
        "weekly_jobs": worker.weekly_jobs_count or 0,
        "total_jobs": worker.total_jobs or 0,
        "recent_settlements": items,
    }
