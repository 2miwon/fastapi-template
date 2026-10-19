import uuid
from typing import Annotated

from fastapi import Depends

from src.auth.dependencies import CurrentUser
from src.database import DbSession
from src.posts import service
from src.posts.exceptions import PostNotFound, PostNotOwned
from src.posts.models import Post


async def valid_post_id(post_id: uuid.UUID, session: DbSession) -> Post:
    post = await service.get_post(session, post_id)
    if post is None:
        raise PostNotFound()
    return post


async def valid_owned_post(
    post: Annotated[Post, Depends(valid_post_id)], user: CurrentUser
) -> Post:
    """Chained on `valid_post_id`: existence is checked first, then ownership."""
    if post.author_id != user.id and not user.is_admin:
        raise PostNotOwned()
    return post


ValidPost = Annotated[Post, Depends(valid_post_id)]
OwnedPost = Annotated[Post, Depends(valid_owned_post)]
