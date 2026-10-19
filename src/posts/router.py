from fastapi import APIRouter, status

from src.auth.dependencies import CurrentUser
from src.database import DbSession
from src.pagination import Page, Pagination
from src.posts import service
from src.posts.dependencies import OwnedPost, ValidPost
from src.posts.schemas import PostCreate, PostResponse, PostUpdate

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("")
async def list_posts(session: DbSession, page: Pagination) -> Page[PostResponse]:
    posts, total = await service.list_posts(session, page)
    return Page(
        items=[PostResponse.model_validate(p) for p in posts],
        total=total,
        limit=page.limit,
        offset=page.offset,
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_post(data: PostCreate, user: CurrentUser, session: DbSession) -> PostResponse:
    post = await service.create_post(session, user, data)
    return PostResponse.model_validate(post)


@router.get("/{post_id}")
async def get_post(post: ValidPost) -> PostResponse:
    return PostResponse.model_validate(post)


@router.patch("/{post_id}")
async def update_post(data: PostUpdate, post: OwnedPost, session: DbSession) -> PostResponse:
    post = await service.update_post(session, post, data)
    return PostResponse.model_validate(post)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post: OwnedPost, session: DbSession) -> None:
    await service.delete_post(session, post)
