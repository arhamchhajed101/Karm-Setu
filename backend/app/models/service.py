from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.db.session import Base


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    cooperative_id = Column(Integer, ForeignKey("cooperatives.id", ondelete="CASCADE"), nullable=False, index=True)
    
    category = Column(String, nullable=False, index=True)  # Plumbing, Electrical, Masonry, Carpentry, Painting, etc.
    name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)
    
    # Pricing model: FIXED, INSPECTION_DIAGNOSTIC, HOURLY
    pricing_model = Column(String, default="FIXED", nullable=False)
    base_price = Column(Float, nullable=False)
    estimated_duration_minutes = Column(Integer, default=60, nullable=False)
    emergency_multiplier = Column(Float, default=1.25, nullable=False)  # 25% surge for priority/emergency dispatch
    
    # Skill requirements for matching
    required_skills = Column(Text, default="[]", nullable=False)  # JSON-encoded array: ["Plumbing"]
    
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    cooperative = relationship("Cooperative", back_populates="services")
    jobs = relationship("Job", back_populates="service")
