from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.db.session import Base


class CooperativeSettlement(Base):
    __tablename__ = "cooperative_settlements"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    cooperative_id = Column(Integer, ForeignKey("cooperatives.id", ondelete="CASCADE"), nullable=False, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Financial breakdown
    gross_amount = Column(Float, nullable=False)
    worker_amount = Column(Float, nullable=False)        # Typically ~80%
    cooperative_amount = Column(Float, nullable=False)   # Typically ~15% operational
    welfare_amount = Column(Float, nullable=False)       # Typically ~5% welfare/insurance fund
    adjustment_amount = Column(Float, default=0.0)       # Deductions, tool allowances, or bonus
    
    # Settlement & Payment states
    payment_method = Column(String, default="ONLINE_SIMULATED", nullable=False)
    payment_status = Column(String, default="PAID", nullable=False)  # PENDING, PAID, REFUNDED
    settlement_status = Column(String, default="SETTLED", nullable=False)  # PENDING, SETTLED, DISPUTED
    
    notes = Column(Text, nullable=True)
    settled_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    job = relationship("Job", back_populates="settlement")
    cooperative = relationship("Cooperative", back_populates="settlements")
    worker = relationship("Worker", back_populates="settlements")
