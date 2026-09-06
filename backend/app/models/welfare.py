from datetime import datetime, date, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship

from app.db.session import Base


class WelfareRecord(Base):
    __tablename__ = "welfare_records"

    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id", ondelete="CASCADE"), nullable=False, index=True)
    cooperative_id = Column(Integer, ForeignKey("cooperatives.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Scheme info (e-Shram PM-SYM, PMSBY Accident Insurance, PMJJBY Life Insurance, State Welfare Board)
    scheme_name = Column(String, nullable=False, index=True)
    policy_number = Column(String, unique=True, nullable=False, index=True)
    status = Column(String, default="ACTIVE", nullable=False)  # ACTIVE, EXPIRING_SOON, EXPIRED, PENDING
    
    coverage_amount = Column(Float, default=200000.0)  # e.g., ₹2,00,000 for PMSBY
    annual_premium = Column(Float, default=20.0)
    
    start_date = Column(Date, default=date.today)
    end_date = Column(Date, nullable=False)
    
    contribution_status = Column(String, default="UP_TO_DATE", nullable=False)  # UP_TO_DATE, DUE, OVERDUE
    last_contribution_date = Column(Date, default=date.today)
    total_welfare_contributed = Column(Float, default=0.0)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    worker = relationship("Worker", back_populates="welfare_records")
    cooperative = relationship("Cooperative", back_populates="welfare_records")
