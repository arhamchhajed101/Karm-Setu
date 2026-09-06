from datetime import datetime, date, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.db.session import Base


class InstitutionalProject(Base):
    __tablename__ = "institutional_projects"

    id = Column(Integer, primary_key=True, index=True)
    client_name = Column(String, nullable=False, index=True)  # e.g., "CPWD Delhi", "Delhi Metro Rail Corp", "Apollo Hospital"
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    cooperative_id = Column(Integer, ForeignKey("cooperatives.id", ondelete="CASCADE"), nullable=False, index=True)
    supervisor_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Workforce planning
    required_headcount = Column(Integer, nullable=False)
    skills_breakdown = Column(Text, default="{}", nullable=False)  # JSON: {"Plumber": 4, "Electrician": 3, "Mason": 8}
    assigned_workers = Column(Text, default="[]", nullable=False)  # JSON: list of worker IDs
    
    # Timeline & Commercials
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    budget = Column(Float, nullable=False)
    amount_disbursed = Column(Float, default=0.0)
    
    status = Column(String, default="PLANNED", nullable=False)  # DRAFT, PLANNED, ACTIVE, COMPLETED, SUSPENDED
    progress_percentage = Column(Float, default=0.0)
    milestones = Column(Text, default="[]", nullable=False)  # JSON list of milestones with completion flags
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    cooperative = relationship("Cooperative", back_populates="institutional_projects")
    supervisor = relationship("User", foreign_keys=[supervisor_id])
