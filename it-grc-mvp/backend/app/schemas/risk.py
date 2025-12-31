from pydantic import BaseModel
from datetime import datetime

class RiskCreate(BaseModel):
    title: str
    description: str = ""
    likelihood: int  # 1-3
    impact: int      # 1-3
    owner_id: int | None = None
    mitigation_plan: str = ""

class RiskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    likelihood: int | None = None
    impact: int | None = None
    owner_id: int | None = None
    mitigation_plan: str | None = None

class RiskOut(BaseModel):
    id: int
    title: str
    description: str
    likelihood: int
    impact: int
    score: int
    owner_id: int | None
    mitigation_plan: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
