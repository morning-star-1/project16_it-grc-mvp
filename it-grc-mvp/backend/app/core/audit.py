from sqlalchemy.orm import Session
from app.models.audit import AuditLog

def write_audit(
    db: Session,
    actor_user_id: int | None,
    action: str,
    entity_type: str,
    entity_id: str,
    ip: str = "",
    details: str = "",
) -> None:
    db.add(AuditLog(
        actor_user_id=actor_user_id,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id),
        ip=ip or "",
        details=details or "",
    ))
    db.commit()
