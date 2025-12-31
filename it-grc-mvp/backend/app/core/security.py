from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import settings

# Use PBKDF2 to avoid bcrypt backend issues on some Windows/Python builds
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def hash_password(pw: str) -> str:
    return pwd_context.hash(pw)

def verify_password(pw: str, pw_hash: str) -> bool:
    return pwd_context.verify(pw, pw_hash)

def create_access_token(subject: str, minutes: int | None = None) -> str:
    exp_minutes = minutes or settings.ACCESS_TOKEN_MINUTES
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=exp_minutes)).timestamp()),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)

def decode_token(token: str) -> dict:
    # rbac.py catches JWTError and converts to 401
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
