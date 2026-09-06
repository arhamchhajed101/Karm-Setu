from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    id: int
    entity_type: str
    entity_id: int
    action: str
    actor_id: Optional[int] = None
    actor_role: Optional[str] = None
    details: dict
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
