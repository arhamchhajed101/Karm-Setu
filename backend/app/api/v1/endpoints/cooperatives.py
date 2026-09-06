import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.deps import get_db, get_current_user, require_role
from app.models.user import User, UserRole
from app.models.cooperative import Cooperative
from app.models.worker import Worker
from app.models.job import Job, JobStatus
from app.schemas.cooperative import (
    CooperativeCreate,
    CooperativeUpdate,
    CooperativeResponse,
    CooperativeKPIs,
)
from app.schemas.worker import WorkerRosterItem

router = APIRouter()


@router.get("", response_model=List[CooperativeResponse])
def list_cooperatives(
    state: Optional[str] = None,
    district: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """
    Lists registered labour cooperatives with optional state/district filtering.
    """
    query = db.query(Cooperative)
    if state:
        query = query.filter(Cooperative.state.ilike(f"%{state}%"))
    if district:
        query = query.filter(Cooperative.district.ilike(f"%{district}%"))
    
    coops = query.offset(skip).limit(limit).all()
    
    results = []
    for c in coops:
        try:
            cats = json.loads(c.service_categories) if isinstance(c.service_categories, str) else (c.service_categories or [])
        except Exception:
            cats = []
        results.append(
            CooperativeResponse(
                id=c.id,
                name=c.name,
                registration_id=c.registration_id,
                state=c.state,
                district=c.district,
                address=c.address,
                pin_code=c.pin_code,
                contact_phone=c.contact_phone,
                contact_email=c.contact_email,
                type=c.type,
                verification_status=c.verification_status,
                service_categories=cats,
                commission_rate=c.commission_rate,
                welfare_contribution_rate=c.welfare_contribution_rate,
                total_members=c.total_members or 0,
                total_jobs_completed=c.total_jobs_completed or 0,
                welfare_fund_pool=c.welfare_fund_pool or 0.0,
                created_at=c.created_at,
            )
        )
    return results


@router.get("/{id}", response_model=CooperativeResponse)
def get_cooperative(id: int, db: Session = Depends(get_db)):
    """
    Retrieves detailed profile of a specific cooperative.
    """
    c = db.query(Cooperative).filter(Cooperative.id == id).first()
    if not c:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cooperative not found")

    try:
        cats = json.loads(c.service_categories) if isinstance(c.service_categories, str) else (c.service_categories or [])
    except Exception:
        cats = []

    return CooperativeResponse(
        id=c.id,
        name=c.name,
        registration_id=c.registration_id,
        state=c.state,
        district=c.district,
        address=c.address,
        pin_code=c.pin_code,
        contact_phone=c.contact_phone,
        contact_email=c.contact_email,
        type=c.type,
        verification_status=c.verification_status,
        service_categories=cats,
        commission_rate=c.commission_rate,
        welfare_contribution_rate=c.welfare_contribution_rate,
        total_members=c.total_members or 0,
        total_jobs_completed=c.total_jobs_completed or 0,
        welfare_fund_pool=c.welfare_fund_pool or 0.0,
        created_at=c.created_at,
    )


@router.post("", response_model=CooperativeResponse, status_code=status.HTTP_201_CREATED)
def create_cooperative(
    coop_in: CooperativeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.COOPERATIVE_ADMIN, UserRole.SUPERVISOR))
):
    """
    Registers a new cooperative society.
    """
    existing = db.query(Cooperative).filter(Cooperative.registration_id == coop_in.registration_id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Registration ID already exists.")

    c = Cooperative(
        name=coop_in.name,
        registration_id=coop_in.registration_id,
        state=coop_in.state,
        district=coop_in.district,
        address=coop_in.address,
        pin_code=coop_in.pin_code,
        contact_phone=coop_in.contact_phone,
        contact_email=coop_in.contact_email,
        type=coop_in.type,
        verification_status=coop_in.verification_status,
        service_categories=json.dumps(coop_in.service_categories),
        commission_rate=coop_in.commission_rate,
        welfare_contribution_rate=coop_in.welfare_contribution_rate,
    )
    db.add(c)
    db.commit()
    db.refresh(c)

    return CooperativeResponse(
        id=c.id,
        name=c.name,
        registration_id=c.registration_id,
        state=c.state,
        district=c.district,
        address=c.address,
        pin_code=c.pin_code,
        contact_phone=c.contact_phone,
        contact_email=c.contact_email,
        type=c.type,
        verification_status=c.verification_status,
        service_categories=coop_in.service_categories,
        commission_rate=c.commission_rate,
        welfare_contribution_rate=c.welfare_contribution_rate,
        total_members=0,
        total_jobs_completed=0,
        welfare_fund_pool=0.0,
        created_at=c.created_at,
    )


@router.put("/{id}", response_model=CooperativeResponse)
def update_cooperative(
    id: int,
    coop_in: CooperativeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.COOPERATIVE_ADMIN))
):
    """
    Updates cooperative parameters (service categories, commission, welfare rates).
    """
    c = db.query(Cooperative).filter(Cooperative.id == id).first()
    if not c:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cooperative not found")

    if coop_in.name is not None:
        c.name = coop_in.name
    if coop_in.address is not None:
        c.address = coop_in.address
    if coop_in.contact_phone is not None:
        c.contact_phone = coop_in.contact_phone
    if coop_in.contact_email is not None:
        c.contact_email = coop_in.contact_email
    if coop_in.service_categories is not None:
        c.service_categories = json.dumps(coop_in.service_categories)
    if coop_in.commission_rate is not None:
        c.commission_rate = coop_in.commission_rate
    if coop_in.welfare_contribution_rate is not None:
        c.welfare_contribution_rate = coop_in.welfare_contribution_rate
    if coop_in.verification_status is not None:
        c.verification_status = coop_in.verification_status

    db.commit()
    db.refresh(c)

    try:
        cats = json.loads(c.service_categories) if isinstance(c.service_categories, str) else (c.service_categories or [])
    except Exception:
        cats = []

    return CooperativeResponse(
        id=c.id,
        name=c.name,
        registration_id=c.registration_id,
        state=c.state,
        district=c.district,
        address=c.address,
        pin_code=c.pin_code,
        contact_phone=c.contact_phone,
        contact_email=c.contact_email,
        type=c.type,
        verification_status=c.verification_status,
        service_categories=cats,
        commission_rate=c.commission_rate,
        welfare_contribution_rate=c.welfare_contribution_rate,
        total_members=c.total_members or 0,
        total_jobs_completed=c.total_jobs_completed or 0,
        welfare_fund_pool=c.welfare_fund_pool or 0.0,
        created_at=c.created_at,
    )


@router.get("/{id}/roster", response_model=List[WorkerRosterItem])
def get_cooperative_roster(
    id: int,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Retrieves the worker roster belonging to this cooperative with availability, trust badges, and weekly workload.
    """
    query = db.query(Worker).filter(Worker.cooperative_id == id)
    if status:
        query = query.filter(Worker.availability_status == status)

    workers = query.all()
    roster = []
    for w in workers:
        try:
            skills = json.loads(w.skills) if isinstance(w.skills, str) else (w.skills or [])
        except Exception:
            skills = []
        roster.append(
            WorkerRosterItem(
                id=w.id,
                name=w.name,
                phone=w.phone,
                skills=skills,
                verification_status=w.verification_status,
                rating=w.rating,
                total_jobs=w.total_jobs,
                weekly_jobs_count=w.weekly_jobs_count,
                availability_status=w.availability_status,
                welfare_status=w.welfare_status,
                latitude=w.latitude,
                longitude=w.longitude,
            )
        )
    return roster


@router.get("/{id}/kpis", response_model=CooperativeKPIs)
def get_cooperative_kpis(id: int, db: Session = Depends(get_db)):
    """
    Generates executive KPIs for the Cooperative Administrator dashboard.
    """
    coop = db.query(Cooperative).filter(Cooperative.id == id).first()
    if not coop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cooperative not found")

    workers = db.query(Worker).filter(Worker.cooperative_id == id).all()
    total_workers = len(workers)
    active_available = sum(1 for w in workers if w.availability_status == "AVAILABLE")
    busy_workers = sum(1 for w in workers if w.availability_status == "BUSY")
    avg_rating = round(sum(w.rating for w in workers) / total_workers, 2) if total_workers > 0 else 5.0

    completed_jobs = (
        db.query(Job)
        .filter(Job.cooperative_id == id, Job.status == JobStatus.COMPLETED)
        .count()
    )
    active_jobs = (
        db.query(Job)
        .filter(
            Job.cooperative_id == id,
            Job.status.in_([JobStatus.REQUESTED, JobStatus.ASSIGNED, JobStatus.ACCEPTED, JobStatus.IN_PROGRESS])
        )
        .count()
    )

    # Calculate total gross revenue
    total_rev = (
        db.query(func.sum(Job.final_price))
        .filter(Job.cooperative_id == id, Job.status == JobStatus.COMPLETED)
        .scalar()
        or 0.0
    )

    return CooperativeKPIs(
        cooperative_id=coop.id,
        name=coop.name,
        total_workers=total_workers,
        active_available_workers=active_available,
        busy_workers=busy_workers,
        total_jobs_completed=completed_jobs or (coop.total_jobs_completed or 0),
        active_jobs_count=active_jobs,
        total_revenue=round(total_rev, 2),
        total_welfare_pool=coop.welfare_fund_pool or 0.0,
        average_worker_rating=avg_rating,
        top_categories=[
            {"category": "Plumbing", "share": 35},
            {"category": "Electrical", "share": 28},
            {"category": "Carpentry", "share": 18},
            {"category": "Masonry", "share": 12},
            {"category": "Painting", "share": 7},
        ],
    )
