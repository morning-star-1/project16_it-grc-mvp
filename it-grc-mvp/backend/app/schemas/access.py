from pydantic import BaseModel
from datetime import datetime

class AccessRequestCreate(BaseModel):
    resource: str
    requested_role: str

class AccessRequestOut(BaseModel):
    id: int
    resource: str
    requested_role: str
    status: str
    requested_by_id: int
    approved_by_id: int | None
    created_at: datetime
    decided_at: datetime | None

    class Config:
        from_attributes = True
