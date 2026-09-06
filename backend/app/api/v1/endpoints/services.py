import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.user import User, UserRole
from app.models.service import Service
from app.models.cooperative import Cooperative
from app.schemas.service import ServiceCreate, ServiceUpdate, ServiceResponse

router = APIRouter()


def _format_service(s: Service) -> ServiceResponse:
    try:
        req_skills = json.loads(s.required_skills) if isinstance(s.required_skills, str) else (s.required_skills or [])
    except Exception:
        req_skills = []

    return ServiceResponse(
        id=s.id,
        cooperative_id=s.cooperative_id,
        cooperative_name=s.cooperative.name if s.cooperative else None,
        category=s.category,
        name=s.name,
        description=s.description,
        pricing_model=s.pricing_model,
        base_price=s.base_price,
        estimated_duration_minutes=s.estimated_duration_minutes,
        emergency_multiplier=s.emergency_multiplier,
        required_skills=req_skills,
        is_active=s.is_active,
        created_at=s.created_at,
    )


@router.get("", response_model=List[ServiceResponse])
def list_services(
    cooperative_id: Optional[int] = None,
    category: Optional[str] = None,
    pricing_model: Optional[str] = None,
    active_only: bool = True,
    db: Session = Depends(get_db),
):
    """
    Lists all services in the cooperative catalogue with optional category and pricing filters.
    """
    query = db.query(Service)
    if active_only:
        query = query.filter(Service.is_active == True)
    if cooperative_id:
        query = query.filter(Service.cooperative_id == cooperative_id)
    if category:
        query = query.filter(Service.category.ilike(f"%{category}%"))
    if pricing_model:
        query = query.filter(Service.pricing_model == pricing_model)

    services = query.all()
    return [_format_service(s) for s in services]


@router.get("/categories")
def list_service_categories(db: Session = Depends(get_db)):
    """
    Returns unique service categories across all active cooperatives.
    """
    cats = db.query(Service.category).filter(Service.is_active == True).distinct().all()
    return [c[0] for c in cats if c[0]]


@router.get("/{id}", response_model=ServiceResponse)
def get_service(id: int, db: Session = Depends(get_db)):
    """
    Retrieves a single service offering.
    """
    s = db.query(Service).filter(Service.id == id).first()
    if not s:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
    return _format_service(s)


@router.post("", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
def create_service(
    service_in: ServiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.COOPERATIVE_ADMIN))
):
    """
    Adds a new service offering to a cooperative's catalogue.
    """
    coop = db.query(Cooperative).filter(Cooperative.id == service_in.cooperative_id).first()
    if not coop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cooperative not found")

    s = Service(
        cooperative_id=service_in.cooperative_id,
        category=service_in.category,
        name=service_in.name,
        description=service_in.description,
        pricing_model=service_in.pricing_model,
        base_price=service_in.base_price,
        estimated_duration_minutes=service_in.estimated_duration_minutes,
        emergency_multiplier=service_in.emergency_multiplier,
        required_skills=json.dumps(service_in.required_skills),
        is_active=service_in.is_active,
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return _format_service(s)


@router.put("/{id}", response_model=ServiceResponse)
def update_service(
    id: int,
    service_in: ServiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.COOPERATIVE_ADMIN))
):
    """
    Updates pricing, base duration, or skills for a service.
    """
    s = db.query(Service).filter(Service.id == id).first()
    if not s:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")

    if service_in.category is not None:
        s.category = service_in.category
    if service_in.name is not None:
        s.name = service_in.name
    if service_in.description is not None:
        s.description = service_in.description
    if service_in.pricing_model is not None:
        s.pricing_model = service_in.pricing_model
    if service_in.base_price is not None:
        s.base_price = service_in.base_price
    if service_in.estimated_duration_minutes is not None:
        s.estimated_duration_minutes = service_in.estimated_duration_minutes
    if service_in.emergency_multiplier is not None:
        s.emergency_multiplier = service_in.emergency_multiplier
    if service_in.required_skills is not None:
        s.required_skills = json.dumps(service_in.required_skills)
    if service_in.is_active is not None:
        s.is_active = service_in.is_active

    db.commit()
    db.refresh(s)
    return _format_service(s)
