from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User, Role, Permission
from app.models.compliance import Framework, Control, ControlMapping

def ensure_role(db: Session, name: str) -> Role:
    r = db.query(Role).filter(Role.name == name).first()
    if not r:
        r = Role(name=name)
        db.add(r)
        db.commit()
        db.refresh(r)
    return r

def ensure_perm(db: Session, code: str) -> Permission:
    p = db.query(Permission).filter(Permission.code == code).first()
    if not p:
        p = Permission(code=code)
        db.add(p)
        db.commit()
        db.refresh(p)
    return p

def attach_perms(db: Session, role: Role, perm_codes: list[str]):
    perms = [ensure_perm(db, c) for c in perm_codes]
    role.permissions = perms
    db.commit()

def ensure_user(db: Session, email: str, full_name: str, password: str) -> User:
    u = db.query(User).filter(User.email == email).first()
    if not u:
        u = User(email=email, full_name=full_name, password_hash=hash_password(password))
        db.add(u)
        db.commit()
        db.refresh(u)
    return u

def ensure_framework(db: Session, name: str) -> Framework:
    f = db.query(Framework).filter(Framework.name == name).first()
    if not f:
        f = Framework(name=name)
        db.add(f)
        db.commit()
        db.refresh(f)
    return f

def ensure_control(db: Session, name: str, desc: str) -> Control:
    c = db.query(Control).filter(Control.name == name).first()
    if not c:
        c = Control(name=name, description=desc)
        db.add(c)
        db.commit()
        db.refresh(c)
    return c

def ensure_mapping(db: Session, control_id: int, framework_id: int, status: str, notes: str):
    m = db.query(ControlMapping).filter(
        ControlMapping.control_id == control_id,
        ControlMapping.framework_id == framework_id
    ).first()
    if not m:
        m = ControlMapping(control_id=control_id, framework_id=framework_id, status=status, notes=notes)
        db.add(m)
        db.commit()
        db.refresh(m)
    return m

def run_seed(db: Session):
    # Roles
    admin = ensure_role(db, "Admin")
    manager = ensure_role(db, "Manager")
    auditor = ensure_role(db, "Auditor")
    employee = ensure_role(db, "Employee")

    # Permissions
    attach_perms(db, admin, [
        "user:read", "user:write",
        "access:read", "access:approve",
        "risk:read", "risk:write",
        "compliance:read", "compliance:write",
        "audit:read",
        "report:export",
    ])
    attach_perms(db, manager, [
        "access:read", "access:approve",
        "risk:read", "risk:write",
        "compliance:read", "compliance:write",
        "report:export",
    ])
    attach_perms(db, auditor, [
        "user:read",
        "access:read",
        "risk:read",
        "compliance:read",
        "audit:read",
        "report:export",
    ])
    attach_perms(db, employee, [
        "access:read",
        "risk:read",
        "compliance:read",
    ])

    # Users
    admin_user = ensure_user(db, "admin@local", "System Admin", "ChangeMe123!")
    mgr_user = ensure_user(db, "manager@local", "IT Manager", "ChangeMe123!")
    aud_user = ensure_user(db, "auditor@local", "Security Auditor", "ChangeMe123!")
    emp_user = ensure_user(db, "employee@local", "Employee", "ChangeMe123!")

    admin_user.roles = [admin]
    mgr_user.roles = [manager]
    aud_user.roles = [auditor]
    emp_user.roles = [employee]
    db.commit()

    # Frameworks
    iso = ensure_framework(db, "ISO 27001")
    soc2 = ensure_framework(db, "SOC 2")
    gdpr = ensure_framework(db, "GDPR")

    # Controls
    c1 = ensure_control(db, "Access Reviews", "Periodic review of user access entitlements.")
    c2 = ensure_control(db, "MFA Enabled", "Multi-factor authentication required for privileged access.")
    c3 = ensure_control(db, "Audit Logging", "Security-relevant events are logged and monitored.")

    # Mappings
    ensure_mapping(db, c1.id, iso.id, "COMPLIANT", "Quarterly reviews scheduled.")
    ensure_mapping(db, c2.id, soc2.id, "COMPLIANT", "MFA enforced for admin roles.")
    ensure_mapping(db, c3.id, gdpr.id, "PARTIAL", "Logging enabled; retention policy in progress.")
