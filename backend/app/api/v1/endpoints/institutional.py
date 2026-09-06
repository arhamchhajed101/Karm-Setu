import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_role
from app.models.user import User, UserRole
from app.models.institutional import InstitutionalProject
from app.models.cooperative import Cooperative
from app.schemas.institutional import (
    InstitutionalProjectCreate,
    InstitutionalProjectUpdate,
    InstitutionalProjectResponse,
)

router = APIRouter()


def _format_project(p: InstitutionalProject) -> InstitutionalProjectResponse:
    try:
        skills = json.loads(p.skills_breakdown) if isinstance(p.skills_breakdown, str) else (p.skills_breakdown or {})
    except Exception:
        skills = {}
    try:
        workers = json.loads(p.assigned_workers) if isinstance(p.assigned_workers, str) else (p.assigned_workers or [])
    except Exception:
        workers = []
    try:
        milestones = json.loads(p.milestones) if isinstance(p.milestones, str) else (p.milestones or [])
    except Exception:
        milestones = []

    return InstitutionalProjectResponse(
        id=p.id,
        client_name=p.client_name,
        title=p.title,
        description=p.description,
        cooperative_id=p.cooperative_id,
        cooperative_name=p.cooperative.name if p.cooperative else None,
        supervisor_id=p.supervisor_id,
        supervisor_name=p.supervisor.full_name if p.supervisor else None,
        required_headcount=p.required_headcount,
        skills_breakdown=skills,
        assigned_workers=workers,
        start_date=p.start_date,
        end_date=p.end_date,
        budget=p.budget,
        amount_disbursed=p.amount_disbursed or 0.0,
        status=p.status,
        progress_percentage=p.progress_percentage or 0.0,
        milestones=milestones,
        created_at=p.created_at,
    )


@router.get("/projects", response_model=List[InstitutionalProjectResponse])
def list_projects(
    cooperative_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Lists institutional and enterprise contracts (CPWD, Metro, Hospitals, Universities).
    """
    query = db.query(InstitutionalProject)
    if cooperative_id:
        query = query.filter(InstitutionalProject.cooperative_id == cooperative_id)
    if status:
        query = query.filter(InstitutionalProject.status == status)

    projects = query.order_by(InstitutionalProject.created_at.desc()).all()
    return [_format_project(p) for p in projects]


@router.get("/projects/{id}", response_model=InstitutionalProjectResponse)
def get_project(id: int, db: Session = Depends(get_db)):
    """
    Retrieves details, milestone checklist, and workforce team roster for an enterprise contract.
    """
    p = db.query(InstitutionalProject).filter(InstitutionalProject.id == id).first()
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return _format_project(p)


@router.post("/projects", response_model=InstitutionalProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    p_in: InstitutionalProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.COOPERATIVE_ADMIN, UserRole.SUPERVISOR))
):
    """
    Registers a new multi-worker institutional contract.
    """
    coop = db.query(Cooperative).filter(Cooperative.id == p_in.cooperative_id).first()
    if not coop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cooperative not found")

    p = InstitutionalProject(
        client_name=p_in.client_name,
        title=p_in.title,
        description=p_in.description,
        cooperative_id=p_in.cooperative_id,
        supervisor_id=p_in.supervisor_id,
        required_headcount=p_in.required_headcount,
        skills_breakdown=json.dumps(p_in.skills_breakdown),
        assigned_workers="[]",
        start_date=p_in.start_date,
        end_date=p_in.end_date,
        budget=p_in.budget,
        status="PLANNED",
        progress_percentage=0.0,
        milestones=json.dumps(p_in.milestones),
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return _format_project(p)


@router.put("/projects/{id}", response_model=InstitutionalProjectResponse)
def update_project(
    id: int,
    p_in: InstitutionalProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.COOPERATIVE_ADMIN, UserRole.SUPERVISOR))
):
    """
    Updates contract progress, milestone status, or team worker assignments.
    """
    p = db.query(InstitutionalProject).filter(InstitutionalProject.id == id).first()
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    if p_in.title is not None:
        p.title = p_in.title
    if p_in.description is not None:
        p.description = p_in.description
    if p_in.supervisor_id is not None:
        p.supervisor_id = p_in.supervisor_id
    if p_in.required_headcount is not None:
        p.required_headcount = p_in.required_headcount
    if p_in.skills_breakdown is not None:
        p.skills_breakdown = json.dumps(p_in.skills_breakdown)
    if p_in.assigned_workers is not None:
        p.assigned_workers = json.dumps(p_in.assigned_workers)
    if p_in.status is not None:
        p.status = p_in.status
    if p_in.progress_percentage is not None:
        p.progress_percentage = p_in.progress_percentage
    if p_in.milestones is not None:
        p.milestones = json.dumps(p_in.milestones)
    if p_in.amount_disbursed is not None:
        p.amount_disbursed = p_in.amount_disbursed

    db.commit()
    db.refresh(p)
    return _format_project(p)
