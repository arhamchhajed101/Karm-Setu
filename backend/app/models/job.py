import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship

from app.db.session import Base


class JobStatus(str, enum.Enum):
    REQUESTED = "REQUESTED"
    ASSIGNED = "ASSIGNED"
    ACCEPTED = "ACCEPTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    DISPUTED = "DISPUTED"


class PaymentStatus(str, enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    SETTLED = "SETTLED"
    REFUNDED = "REFUNDED"


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    booking_ref = Column(String, unique=True, nullable=False, index=True)  # e.g. KS-2026-1001
    
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    service_id = Column(Integer, ForeignKey("services.id", ondelete="RESTRICT"), nullable=False, index=True)
    cooperative_id = Column(Integer, ForeignKey("cooperatives.id", ondelete="RESTRICT"), nullable=False, index=True)
    assigned_worker_id = Column(Integer, ForeignKey("workers.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # State tracking
    status = Column(Enum(JobStatus), default=JobStatus.REQUESTED, nullable=False, index=True)
    slot_start = Column(DateTime, nullable=False)
    slot_end = Column(DateTime, nullable=False)
    
    # Site location
    address = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    is_emergency = Column(Boolean, default=False, nullable=False)
    
    # Pricing and payment
    price_estimate = Column(Float, nullable=False)
    final_price = Column(Float, nullable=True)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    payment_method = Column(String, default="ONLINE_SIMULATED", nullable=False)  # ONLINE_SIMULATED, CASH_ON_DELIVERY, DIRECT_UPI
    
    # Context & Notes
    customer_notes = Column(Text, nullable=True)
    worker_notes = Column(Text, nullable=True)
    cancellation_reason = Column(String, nullable=True)
    
    # Supervisor sign-off (P1 institutional/verified jobs)
    supervisor_verified = Column(Boolean, default=False)
    supervisor_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    assigned_at = Column(DateTime, nullable=True)
    accepted_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    customer = relationship("Customer", back_populates="jobs")
    service = relationship("Service", back_populates="jobs")
    cooperative = relationship("Cooperative", back_populates="jobs")
    assigned_worker = relationship("Worker", back_populates="assigned_jobs")
    allocation_scores = relationship("AllocationScore", back_populates="job", cascade="all, delete-orphan")
    settlement = relationship("CooperativeSettlement", back_populates="job", uselist=False, cascade="all, delete-orphan")
    review = relationship("Review", back_populates="job", uselist=False, cascade="all, delete-orphan")
