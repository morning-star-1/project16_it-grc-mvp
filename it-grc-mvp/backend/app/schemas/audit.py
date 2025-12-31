from pydantic import BaseModel
from datetime import datetime

class AuditOut(BaseModel):
    id: int
    actor_user_id: int | None
    action: str
    entity_type: str
    entity_id: str
    ip: str
    details: str
    created_at: datetime

    class Config:
        from_attributes = True
