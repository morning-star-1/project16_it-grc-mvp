from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = ""
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    roles: list[str]

    class Config:
        from_attributes = True

class RoleAssign(BaseModel):
    roles: list[str]
