from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.db.session import Base


class AllocationScore(Base):
    __tablename__ = "allocation_scores"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Transparent weighted breakdown (0 - 100 base)
    skill_score = Column(Float, nullable=False)        # 30% weight: exact trade & certification match
    availability_score = Column(Float, nullable=False) # 20% weight: schedule slot fit & buffer
    distance_score = Column(Float, nullable=False)     # 15% weight: proximity to site (km)
    reliability_score = Column(Float, nullable=False)  # 15% weight: rating & completion rate
    workload_score = Column(Float, nullable=False)     # 10% weight: fatigue prevention
    fairness_score = Column(Float, nullable=False)     # 10% weight: utilization equalization
    
    total_score = Column(Float, nullable=False, index=True)
    is_assigned = Column(Boolean, default=False, nullable=False)
    
    # Explainable AI summary (JSON string + narrative text)
    explanation = Column(Text, nullable=False)
    evaluated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    job = relationship("Job", back_populates="allocation_scores")
    worker = relationship("Worker", back_populates="allocation_scores")
