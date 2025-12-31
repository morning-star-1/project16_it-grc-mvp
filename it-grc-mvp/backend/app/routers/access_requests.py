from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.access import AccessRequest
from app.schemas.access import AccessRequestCreate, AccessRequestOut
from app.core.rbac import get_current_user, require_permissions
from app.core.audit import write_audit

router = APIRouter(prefix="/access-requests", tags=["access_requests"])

@router.post("", response_model=AccessRequestOut)
def create_access_request(
    payload: AccessRequestCreate,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    ar = AccessRequest(
        resource=payload.resource,
        requested_role=payload.requested_role,
        status="PENDING",
        requested_by_id=user.id,
        approved_by_id=None,
    )
    db.add(ar)
    db.commit()
    db.refresh(ar)

    write_audit(db, user.id, "ACCESS_REQUEST_CREATE", "AccessRequest", str(ar.id), ip=request.client.host if request.client else "", details=f"resource={ar.resource}")

    return ar

@router.get("", response_model=list[AccessRequestOut])
def list_access_requests(db: Session = Depends(get_db), actor=Depends(require_permissions("access:read"))):
    return db.query(AccessRequest).order_by(AccessRequest.created_at.desc()).all()

@router.post("/{req_id}/approve", response_model=AccessRequestOut)
def approve(req_id: int, request: Request, db: Session = Depends(get_db), actor=Depends(require_permissions("access:approve"))):
    ar = db.query(AccessRequest).filter(AccessRequest.id == req_id).first()
    if not ar:
        raise HTTPException(status_code=404, detail="Request not found")
    if ar.status != "PENDING":
        raise HTTPException(status_code=400, detail="Request already decided")

    ar.status = "APPROVED"
    ar.approved_by_id = actor.id
    ar.decided_at = datetime.utcnow()
    db.commit()
    db.refresh(ar)

    write_audit(db, actor.id, "ACCESS_REQUEST_APPROVE", "AccessRequest", str(ar.id), ip=request.client.host if request.client else "")

    return ar

@router.post("/{req_id}/deny", response_model=AccessRequestOut)
def deny(req_id: int, request: Request, db: Session = Depends(get_db), actor=Depends(require_permissions("access:approve"))):
    ar = db.query(AccessRequest).filter(AccessRequest.id == req_id).first()
    if not ar:
        raise HTTPException(status_code=404, detail="Request not found")
    if ar.status != "PENDING":
        raise HTTPException(status_code=400, detail="Request already decided")

    ar.status = "DENIED"
    ar.approved_by_id = actor.id
    ar.decided_at = datetime.utcnow()
    db.commit()
    db.refresh(ar)

    write_audit(db, actor.id, "ACCESS_REQUEST_DENY", "AccessRequest", str(ar.id), ip=request.client.host if request.client else "")

    return ar
