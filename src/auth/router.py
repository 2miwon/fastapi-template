from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from src.auth import service
from src.auth.dependencies import CurrentUser, valid_user_create
from src.auth.exceptions import InvalidCredentials
from src.auth.schemas import AccessTokenResponse, UserCreate, UserResponse
from src.auth.security import create_access_token
from src.database import DbSession

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/users", status_code=status.HTTP_201_CREATED)
async def register_user(
    data: Annotated[UserCreate, Depends(valid_user_create)], session: DbSession
) -> UserResponse:
    user = await service.create_user(session, data)
    return UserResponse.model_validate(user)


@router.post("/token")
async def issue_access_token(
    form: Annotated[OAuth2PasswordRequestForm, Depends()], session: DbSession
) -> AccessTokenResponse:
    user = await service.authenticate(session, form.username, form.password)
    if user is None:
        raise InvalidCredentials()
    return AccessTokenResponse(access_token=create_access_token(user))


@router.get("/users/me")
async def get_my_account(user: CurrentUser) -> UserResponse:
    return UserResponse.model_validate(user)
