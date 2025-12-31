from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.audit import AuditLog
from app.schemas.audit import AuditOut
from app.core.rbac import require_permissions

router = APIRouter(prefix="/audit", tags=["audit"])

@router.get("", response_model=list[AuditOut])
def list_audit(db: Session = Depends(get_db), actor=Depends(require_permissions("audit:read"))):
    return db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(500).all()
