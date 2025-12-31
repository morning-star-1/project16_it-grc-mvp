from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User, Role
from app.schemas.user import UserCreate, UserOut, RoleAssign
from app.core.security import hash_password
from app.core.rbac import require_permissions
from app.core.audit import write_audit

router = APIRouter(prefix="/users", tags=["users"])

@router.post("", response_model=UserOut)
def create_user(payload: UserCreate, db: Session = Depends(get_db), actor=Depends(require_permissions("user:write"))):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=409, detail="Email already exists")

    u = User(email=payload.email, full_name=payload.full_name, password_hash=hash_password(payload.password))
    db.add(u)
    db.commit()
    db.refresh(u)

    write_audit(db, actor.id, "USER_CREATE", "User", str(u.id), details=f"email={u.email}")

    return UserOut(id=u.id, email=u.email, full_name=u.full_name, roles=[r.name for r in u.roles])

@router.get("", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), actor=Depends(require_permissions("user:read"))):
    users = db.query(User).all()
    return [UserOut(id=u.id, email=u.email, full_name=u.full_name, roles=[r.name for r in u.roles]) for u in users]

@router.post("/{user_id}/roles", response_model=UserOut)
def assign_roles(user_id: int, payload: RoleAssign, db: Session = Depends(get_db), actor=Depends(require_permissions("user:write"))):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")

    roles = db.query(Role).filter(Role.name.in_(payload.roles)).all()
    if len(roles) != len(set(payload.roles)):
        found = {r.name for r in roles}
        missing = [r for r in payload.roles if r not in found]
        raise HTTPException(status_code=400, detail=f"Unknown roles: {missing}")

    u.roles = roles
    db.commit()
    db.refresh(u)

    write_audit(db, actor.id, "USER_ROLE_ASSIGN", "User", str(u.id), details="roles=" + ",".join(payload.roles))

    return UserOut(id=u.id, email=u.email, full_name=u.full_name, roles=[r.name for r in u.roles])
