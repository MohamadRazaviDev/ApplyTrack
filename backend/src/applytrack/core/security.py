"""JWT token creation and password hashing helpers."""

from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from applytrack.core.config import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    claims = {"sub": str(subject), "exp": expire, "iat": now}
    return jwt.encode(claims, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)
