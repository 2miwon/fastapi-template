from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from src.auth.config import auth_settings
from src.auth.exceptions import InvalidToken
from src.auth.models import User
from src.auth.schemas import JWTData

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)


def create_access_token(user: User, expires_delta: timedelta | None = None) -> str:
    expire = datetime.now(UTC) + (expires_delta or timedelta(minutes=auth_settings.JWT_EXP))
    payload = {"sub": str(user.id), "is_admin": user.is_admin, "exp": expire}
    return jwt.encode(payload, auth_settings.JWT_SECRET, algorithm=auth_settings.JWT_ALG)


def decode_access_token(token: str) -> JWTData:
    try:
        payload = jwt.decode(token, auth_settings.JWT_SECRET, algorithms=[auth_settings.JWT_ALG])
    except jwt.PyJWTError as exc:
        raise InvalidToken() from exc
    return JWTData.model_validate(payload)
