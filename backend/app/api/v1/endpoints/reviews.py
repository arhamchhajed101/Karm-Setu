import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.job import Job, JobStatus
from app.models.worker import Worker
from app.models.customer import Customer
from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewResponse

router = APIRouter()


def _format_review(r: Review) -> ReviewResponse:
    try:
        tags = json.loads(r.tags) if isinstance(r.tags, str) else (r.tags or [])
    except Exception:
        tags = []

    return ReviewResponse(
        id=r.id,
        job_id=r.job_id,
        customer_id=r.customer_id,
        customer_name=r.customer.name if r.customer else None,
        worker_id=r.worker_id,
        worker_name=r.worker.name if r.worker else None,
        rating=r.rating,
        comment=r.comment,
        tags=tags,
        created_at=r.created_at,
    )


@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def submit_review(
    review_in: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submits a customer rating and review for a completed service booking.
    Updates worker's aggregate rating and reliability score.
    """
    job = db.query(Job).filter(Job.id == review_in.job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    if not job.assigned_worker_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Job has no worker assigned")

    customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()
    if not customer:
        customer = Customer(
            user_id=current_user.id,
            name=current_user.full_name,
            phone=current_user.phone or "",
            email=current_user.email,
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)

    existing = db.query(Review).filter(Review.job_id == job.id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Review already submitted for this job")

    review = Review(
        job_id=job.id,
        customer_id=customer.id,
        worker_id=job.assigned_worker_id,
        rating=review_in.rating,
        comment=review_in.comment,
        tags=json.dumps(review_in.tags),
    )
    db.add(review)

    # Recompute worker rating
    worker = db.query(Worker).filter(Worker.id == job.assigned_worker_id).first()
    if worker:
        all_ratings = db.query(Review.rating).filter(Review.worker_id == worker.id).all()
        ratings_list = [r[0] for r in all_ratings] + [review_in.rating]
        worker.rating = round(sum(ratings_list) / len(ratings_list), 2)

    db.commit()
    db.refresh(review)
    return _format_review(review)


@router.get("/worker/{worker_id}", response_model=List[ReviewResponse])
def get_worker_reviews(worker_id: int, db: Session = Depends(get_db)):
    """
    Lists customer reviews and testimonials for a specific worker.
    """
    reviews = db.query(Review).filter(Review.worker_id == worker_id).order_by(Review.created_at.desc()).all()
    return [_format_review(r) for r in reviews]
