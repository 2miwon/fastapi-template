from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from src.auth import service
from src.auth.exceptions import EmailTaken, InactiveUser, InvalidToken
from src.auth.models import User
from src.auth.schemas import JWTData, UserCreate
from src.auth.security import decode_access_token
from src.database import DbSession
from src.exceptions import PermissionDenied

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


async def valid_user_create(data: UserCreate, session: DbSession) -> UserCreate:
    if await service.get_user_by_email(session, data.email):
        raise EmailTaken()
    return data


async def parse_jwt_data(token: Annotated[str, Depends(oauth2_scheme)]) -> JWTData:
    return decode_access_token(token)


async def get_current_user(
    jwt_data: Annotated[JWTData, Depends(parse_jwt_data)], session: DbSession
) -> User:
    user = await service.get_user_by_id(session, jwt_data.user_id)
    if user is None:
        raise InvalidToken()
    if not user.is_active:
        raise InactiveUser()
    return user


async def get_current_admin(user: Annotated[User, Depends(get_current_user)]) -> User:
    if not user.is_admin:
        raise PermissionDenied()
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentAdmin = Annotated[User, Depends(get_current_admin)]
