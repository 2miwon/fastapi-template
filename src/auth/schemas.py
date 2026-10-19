import re
import uuid
from datetime import datetime

from pydantic import EmailStr, Field, field_validator

from src.auth.constants import PASSWORD_PATTERN
from src.schemas import CustomModel


class UserCreate(CustomModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def valid_password(cls, password: str) -> str:
        if not re.match(PASSWORD_PATTERN, password):
            raise ValueError("Password must contain at least one letter and one digit")
        return password


class UserResponse(CustomModel):
    id: uuid.UUID
    email: EmailStr
    is_active: bool
    is_admin: bool
    created_at: datetime


class AccessTokenResponse(CustomModel):
    access_token: str
    token_type: str = "bearer"  # noqa: S105


class JWTData(CustomModel):
    user_id: uuid.UUID = Field(alias="sub")
    is_admin: bool = False
