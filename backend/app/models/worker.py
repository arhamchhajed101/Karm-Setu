from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.db.session import Base


class Worker(Base):
    __tablename__ = "workers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    cooperative_id = Column(Integer, ForeignKey("cooperatives.id", ondelete="CASCADE"), nullable=False, index=True)
    
    name = Column(String, nullable=False, index=True)
    phone = Column(String, nullable=False)
    photo_url = Column(String, nullable=True)
    
    # Skills, Experience & Certification
    skills = Column(Text, default="[]", nullable=False)  # JSON-encoded array: ["Plumbing", "Pipe Fitting"]
    experience_years = Column(Integer, default=1)
    certificates = Column(Text, default="[]", nullable=False)  # JSON-encoded array of certificate objects
    
    # Trust & Verification (Police/Admin verification reference)
    verification_status = Column(String, default="VERIFIED", nullable=False)  # VERIFIED, PENDING, NOT_VERIFIED
    verification_ref_id = Column(String, nullable=True)
    police_station_jurisdiction = Column(String, nullable=True)
    
    # Performance & Reliability
    rating = Column(Float, default=4.8, nullable=False)
    total_jobs = Column(Integer, default=0, nullable=False)
    weekly_jobs_count = Column(Integer, default=0, nullable=False)
    reliability_score = Column(Float, default=0.95, nullable=False)  # Completion rate metric (0.0 to 1.0)
    
    # Real-time state & Geolocation
    availability_status = Column(String, default="AVAILABLE", nullable=False)  # AVAILABLE, BUSY, OFF_DUTY
    latitude = Column(Float, default=28.6139, nullable=False)
    longitude = Column(Float, default=77.2090, nullable=False)
    address = Column(String, nullable=True)
    
    # Welfare status
    welfare_status = Column(String, default="ACTIVE", nullable=False)  # ACTIVE, EXPIRING_SOON, EXPIRED, PENDING
    total_earnings = Column(Float, default=0.0, nullable=False)
    welfare_balance = Column(Float, default=0.0, nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="worker_profile")
    cooperative = relationship("Cooperative", back_populates="workers")
    assigned_jobs = relationship("Job", back_populates="assigned_worker")
    allocation_scores = relationship("AllocationScore", back_populates="worker")
    settlements = relationship("CooperativeSettlement", back_populates="worker")
    welfare_records = relationship("WelfareRecord", back_populates="worker", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="worker")
