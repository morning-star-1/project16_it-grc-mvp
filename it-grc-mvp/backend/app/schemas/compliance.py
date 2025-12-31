from pydantic import BaseModel

class FrameworkCreate(BaseModel):
    name: str

class ControlCreate(BaseModel):
    name: str
    description: str = ""

class ControlMappingCreate(BaseModel):
    control_id: int
    framework_id: int
    status: str = "PARTIAL"
    notes: str = ""

class FrameworkOut(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True

class ControlOut(BaseModel):
    id: int
    name: str
    description: str
    class Config:
        from_attributes = True

class ControlMappingOut(BaseModel):
    id: int
    control_id: int
    framework_id: int
    status: str
    notes: str
    class Config:
        from_attributes = True
