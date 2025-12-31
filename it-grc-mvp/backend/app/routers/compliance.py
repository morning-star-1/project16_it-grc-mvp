from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.compliance import Framework, Control, ControlMapping
from app.schemas.compliance import (
    FrameworkCreate, ControlCreate, ControlMappingCreate,
    FrameworkOut, ControlOut, ControlMappingOut
)
from app.core.rbac import require_permissions
from app.core.audit import write_audit

router = APIRouter(prefix="/compliance", tags=["compliance"])

@router.post("/frameworks", response_model=FrameworkOut)
def create_framework(payload: FrameworkCreate, request: Request, db: Session = Depends(get_db), actor=Depends(require_permissions("compliance:write"))):
    if db.query(Framework).filter(Framework.name == payload.name).first():
        raise HTTPException(status_code=409, detail="Framework exists")
    f = Framework(name=payload.name)
    db.add(f)
    db.commit()
    db.refresh(f)
    write_audit(db, actor.id, "FRAMEWORK_CREATE", "Framework", str(f.id), ip=request.client.host if request.client else "")
    return f

@router.get("/frameworks", response_model=list[FrameworkOut])
def list_frameworks(db: Session = Depends(get_db), actor=Depends(require_permissions("compliance:read"))):
    return db.query(Framework).order_by(Framework.name.asc()).all()

@router.post("/controls", response_model=ControlOut)
def create_control(payload: ControlCreate, request: Request, db: Session = Depends(get_db), actor=Depends(require_permissions("compliance:write"))):
    if db.query(Control).filter(Control.name == payload.name).first():
        raise HTTPException(status_code=409, detail="Control exists")
    c = Control(name=payload.name, description=payload.description)
    db.add(c)
    db.commit()
    db.refresh(c)
    write_audit(db, actor.id, "CONTROL_CREATE", "Control", str(c.id), ip=request.client.host if request.client else "")
    return c

@router.get("/controls", response_model=list[ControlOut])
def list_controls(db: Session = Depends(get_db), actor=Depends(require_permissions("compliance:read"))):
    return db.query(Control).order_by(Control.name.asc()).all()

@router.post("/mappings", response_model=ControlMappingOut)
def create_mapping(payload: ControlMappingCreate, request: Request, db: Session = Depends(get_db), actor=Depends(require_permissions("compliance:write"))):
    # basic existence checks
    if not db.query(Control).filter(Control.id == payload.control_id).first():
        raise HTTPException(status_code=400, detail="Unknown control_id")
    if not db.query(Framework).filter(Framework.id == payload.framework_id).first():
        raise HTTPException(status_code=400, detail="Unknown framework_id")

    m = ControlMapping(
        control_id=payload.control_id,
        framework_id=payload.framework_id,
        status=payload.status,
        notes=payload.notes,
    )
    db.add(m)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=409, detail="Mapping already exists")
    db.refresh(m)

    write_audit(db, actor.id, "CONTROL_MAPPING_CREATE", "ControlMapping", str(m.id), ip=request.client.host if request.client else "")
    return m

@router.get("/mappings", response_model=list[ControlMappingOut])
def list_mappings(db: Session = Depends(get_db), actor=Depends(require_permissions("compliance:read"))):
    return db.query(ControlMapping).order_by(ControlMapping.id.desc()).all()
