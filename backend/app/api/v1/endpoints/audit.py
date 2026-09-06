import json
from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.user import User, UserRole
from app.models.audit import AuditLog
from app.schemas.audit import AuditLogResponse

router = APIRouter()


@router.get("/logs", response_model=List[AuditLogResponse])
def list_audit_logs(
    entity_type: Optional[str] = None,
    action: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.COOPERATIVE_ADMIN, UserRole.SUPERVISOR))
):
    """
    Returns audit trail records for compliance and regulatory inspections.
    """
    query = db.query(AuditLog)
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    if action:
        query = query.filter(AuditLog.action.ilike(f"%{action}%"))

    logs = query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
    results = []
    for l in logs:
        try:
            details = json.loads(l.details) if isinstance(l.details, str) else (l.details or {})
        except Exception:
            details = {}
        results.append(
            AuditLogResponse(
                id=l.id,
                entity_type=l.entity_type,
                entity_id=l.entity_id,
                action=l.action,
                actor_id=l.actor_id,
                actor_role=l.actor_role,
                details=details,
                timestamp=l.timestamp,
            )
        )
    return results
