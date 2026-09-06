from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Text

from app.db.session import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String, nullable=False, index=True)  # "JOB", "WORKER", "SETTLEMENT", "ALLOCATION"
    entity_id = Column(Integer, nullable=False, index=True)
    action = Column(String, nullable=False, index=True)       # "STATUS_CHANGE", "ASSIGNMENT", "SETTLED", "VERIFIED"
    actor_id = Column(Integer, nullable=True)
    actor_role = Column(String, nullable=True)
    details = Column(Text, default="{}", nullable=False)      # JSON payload of diff or context
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
