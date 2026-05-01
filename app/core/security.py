from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import timedelta

from app.core.config import settings
from app.utils.time import utcnow

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


# ---------- PASSWORD ----------
def get_hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return pwd_context.verify(plain, hashed)
    except Exception:
        return False
        
hash_password = get_password_hash

# ---------- ACCESS TOKEN ----------
def create_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),   # обов'язково поле sub
        "type": "access",
        "exp": utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# ---------- REFRESH TOKEN ----------
def create_refresh_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# ---------- DECODE ----------
def decode_token(token: str) -> dict:
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
    except JWTError:
        return {}   # якщо токен невалідний


def decode_refresh_token(token: str) -> dict | None:
    try:
        payload = decode_token(token)
        if payload.get("type") == "refresh":
            return payload
        return None
    except Exception:
        return None
