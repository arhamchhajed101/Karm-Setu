from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User, UserRole
from app.models.customer import Customer
from app.models.job import Job
from app.schemas.customer import CustomerCreate, CustomerResponse
from app.schemas.job import JobResponse

router = APIRouter()


@router.get("/me", response_model=CustomerResponse)
def get_customer_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves current customer's profile and default address/coordinates.
    """
    customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()
    if not customer:
        # Create a default customer record if missing
        customer = Customer(
            user_id=current_user.id,
            name=current_user.full_name,
            phone=current_user.phone or "",
            email=current_user.email,
            city="Delhi",
            latitude=28.6139,
            longitude=77.2090,
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)
    return customer


@router.put("/me", response_model=CustomerResponse)
def update_customer_profile(
    customer_in: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Updates customer address, phone, or location.
    """
    customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()
    if not customer:
        customer = Customer(user_id=current_user.id, name=customer_in.name, phone=customer_in.phone, email=customer_in.email)
        db.add(customer)

    customer.name = customer_in.name
    customer.phone = customer_in.phone
    customer.address = customer_in.address
    customer.city = customer_in.city
    customer.latitude = customer_in.latitude
    customer.longitude = customer_in.longitude

    db.commit()
    db.refresh(customer)
    return customer


@router.get("/me/bookings", response_model=List[JobResponse])
def get_customer_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves all bookings made by this customer.
    """
    customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()
    if not customer:
        return []

    jobs = db.query(Job).filter(Job.customer_id == customer.id).order_by(Job.created_at.desc()).all()
    results = []
    for j in jobs:
        results.append(
            JobResponse(
                id=j.id,
                booking_ref=j.booking_ref,
                customer_id=j.customer_id,
                customer_name=customer.name,
                customer_phone=customer.phone,
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
        )
    return results
