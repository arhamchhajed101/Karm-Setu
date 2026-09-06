import json
from typing import Any, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.audit import AuditLog


class AuditService:
    """
    Centralized Audit Trail Logger for KarmSetu compliance and trust records.
    """

    @classmethod
    def log_event(
        cls,
        db: Session,
        entity_type: str,
        entity_id: int,
        action: str,
        actor_id: Optional[int] = None,
        actor_role: Optional[str] = None,
        details: Optional[dict] = None,
    ) -> AuditLog:
        log_entry = AuditLog(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            actor_id=actor_id,
            actor_role=actor_role,
            details=json.dumps(details or {}),
            timestamp=datetime.now(timezone.utc),
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        return log_entry
