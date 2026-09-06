from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import relationship

from app.db.session import Base


class Cooperative(Base):
    __tablename__ = "cooperatives"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    registration_id = Column(String, unique=True, nullable=False, index=True)
    state = Column(String, nullable=False, index=True)
    district = Column(String, nullable=False, index=True)
    address = Column(String, nullable=True)
    pin_code = Column(String, nullable=True)
    contact_phone = Column(String, nullable=True)
    contact_email = Column(String, nullable=True)
    type = Column(String, default="Labour Contract Society", nullable=False)
    verification_status = Column(String, default="VERIFIED", nullable=False)  # VERIFIED, PENDING, UNDER_REVIEW
    service_categories = Column(Text, default="[]", nullable=False)  # JSON-encoded array of category strings
    
    # Financial settlement defaults
    commission_rate = Column(Float, default=0.15, nullable=False)  # 15% cooperative operational retention
    welfare_contribution_rate = Column(Float, default=0.05, nullable=False)  # 5% allocated to worker welfare fund
    
    # Aggregated metrics for fast reporting
    total_members = Column(Integer, default=0)
    total_jobs_completed = Column(Integer, default=0)
    welfare_fund_pool = Column(Float, default=0.0)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    workers = relationship("Worker", back_populates="cooperative", cascade="all, delete-orphan")
    services = relationship("Service", back_populates="cooperative", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="cooperative")
    settlements = relationship("CooperativeSettlement", back_populates="cooperative")
    welfare_records = relationship("WelfareRecord", back_populates="cooperative")
    institutional_projects = relationship("InstitutionalProject", back_populates="cooperative")
