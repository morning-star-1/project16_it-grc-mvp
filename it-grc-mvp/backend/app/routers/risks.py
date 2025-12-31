from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.risk import Risk
from app.schemas.risk import RiskCreate, RiskOut, RiskUpdate
from app.core.rbac import get_current_user, require_permissions
from app.core.audit import write_audit

router = APIRouter(prefix="/risks", tags=["risks"])

def compute_score(likelihood: int, impact: int) -> int:
    return int(likelihood) * int(impact)

def validate_scale(v: int, field: str):
    if v < 1 or v > 3:
        raise HTTPException(status_code=400, detail=f"{field} must be 1..3")

@router.post("", response_model=RiskOut)
def create_risk(payload: RiskCreate, request: Request, db: Session = Depends(get_db), actor=Depends(require_permissions("risk:write"))):
    validate_scale(payload.likelihood, "likelihood")
    validate_scale(payload.impact, "impact")
    r = Risk(
        title=payload.title,
        description=payload.description,
        likelihood=payload.likelihood,
        impact=payload.impact,
        score=compute_score(payload.likelihood, payload.impact),
        owner_id=payload.owner_id,
        mitigation_plan=payload.mitigation_plan,
        updated_at=datetime.utcnow(),
    )
    db.add(r)
    db.commit()
    db.refresh(r)

    write_audit(db, actor.id, "RISK_CREATE", "Risk", str(r.id), ip=request.client.host if request.client else "", details=f"score={r.score}")
    return r

@router.get("", response_model=list[RiskOut])
def list_risks(db: Session = Depends(get_db), actor=Depends(require_permissions("risk:read"))):
    return db.query(Risk).order_by(Risk.score.desc(), Risk.updated_at.desc()).all()

@router.patch("/{risk_id}", response_model=RiskOut)
def update_risk(
    risk_id: int,
    payload: RiskUpdate,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    r = db.query(Risk).filter(Risk.id == risk_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Risk not found")

    # Owner OR manager/admin permission
    # If not owner, require risk:write
    if r.owner_id != user.id:
        # This will 403 if missing
        require_permissions("risk:write")(user)

    if payload.likelihood is not None:
        validate_scale(payload.likelihood, "likelihood")
        r.likelihood = payload.likelihood
    if payload.impact is not None:
        validate_scale(payload.impact, "impact")
        r.impact = payload.impact
    if payload.title is not None:
        r.title = payload.title
    if payload.description is not None:
        r.description = payload.description
    if payload.owner_id is not None:
        r.owner_id = payload.owner_id
    if payload.mitigation_plan is not None:
        r.mitigation_plan = payload.mitigation_plan

    r.score = compute_score(r.likelihood, r.impact)
    r.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(r)

    write_audit(db, user.id, "RISK_UPDATE", "Risk", str(r.id), ip=request.client.host if request.client else "", details=f"score={r.score}")
    return r
