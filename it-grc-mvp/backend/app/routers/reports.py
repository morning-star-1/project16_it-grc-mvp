import csv
from io import StringIO
from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.rbac import require_permissions
from app.models.access import AccessRequest
from app.models.risk import Risk
from app.models.compliance import ControlMapping, Control, Framework

router = APIRouter(prefix="/reports", tags=["reports"])

def csv_response(filename: str, rows: list[dict]):
    buf = StringIO()
    if not rows:
        writer = csv.writer(buf)
        writer.writerow(["no_data"])
    else:
        writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return Response(
        content=buf.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

@router.get("/access-reviews")
def access_reviews(db: Session = Depends(get_db), actor=Depends(require_permissions("report:export"))):
    q = db.query(AccessRequest).order_by(AccessRequest.created_at.desc()).all()
    rows = [{
        "id": a.id,
        "resource": a.resource,
        "requested_role": a.requested_role,
        "status": a.status,
        "requested_by_id": a.requested_by_id,
        "approved_by_id": a.approved_by_id,
        "created_at": a.created_at.isoformat(),
        "decided_at": a.decided_at.isoformat() if a.decided_at else "",
    } for a in q]
    return csv_response("access_reviews.csv", rows)

@router.get("/risk-summary")
def risk_summary(db: Session = Depends(get_db), actor=Depends(require_permissions("report:export"))):
    q = db.query(Risk).order_by(Risk.score.desc(), Risk.updated_at.desc()).all()
    rows = [{
        "id": r.id,
        "title": r.title,
        "likelihood": r.likelihood,
        "impact": r.impact,
        "score": r.score,
        "owner_id": r.owner_id or "",
        "updated_at": r.updated_at.isoformat(),
    } for r in q]
    return csv_response("risk_summary.csv", rows)

@router.get("/compliance-gap")
def compliance_gap(db: Session = Depends(get_db), actor=Depends(require_permissions("report:export"))):
    q = (
        db.query(ControlMapping, Control, Framework)
        .join(Control, Control.id == ControlMapping.control_id)
        .join(Framework, Framework.id == ControlMapping.framework_id)
        .order_by(Framework.name.asc(), Control.name.asc())
        .all()
    )
    rows = [{
        "framework": f.name,
        "control": c.name,
        "status": m.status,
        "notes": m.notes,
    } for (m, c, f) in q]
    return csv_response("compliance_gap.csv", rows)
