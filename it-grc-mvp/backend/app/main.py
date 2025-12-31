from fastapi import FastAPI
from sqlalchemy.orm import Session

from app.db.session import engine, SessionLocal
from app.db.base import Base

# Import models so metadata is complete
from app.models import user as _user
from app.models import access as _access
from app.models import risk as _risk
from app.models import compliance as _compliance
from app.models import audit as _audit

from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.access_requests import router as access_router
from app.routers.risks import router as risks_router
from app.routers.compliance import router as compliance_router
from app.routers.reports import router as reports_router
from app.routers.audit import router as audit_router

from app.seed import run_seed

app = FastAPI(title="IT Governance / Risk Management (GRC) MVP")

@app.on_event("startup")
def on_startup():
    # Create tables (MVP approach; for production use Alembic migrations)
    Base.metadata.create_all(bind=engine)

    # Seed initial data
    db: Session = SessionLocal()
    try:
        run_seed(db)
    finally:
        db.close()

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(access_router)
app.include_router(risks_router)
app.include_router(compliance_router)
app.include_router(reports_router)
app.include_router(audit_router)
