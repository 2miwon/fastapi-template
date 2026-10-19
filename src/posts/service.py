import uuid
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.pagination import PaginationParams
from src.posts.models import Post
from src.posts.schemas import PostCreate, PostUpdate


async def list_posts(session: AsyncSession, page: PaginationParams) -> tuple[Sequence[Post], int]:
    total = await session.scalar(select(func.count()).select_from(Post)) or 0
    rows = await session.scalars(
        select(Post).order_by(Post.created_at.desc()).limit(page.limit).offset(page.offset)
    )
    return rows.all(), total


async def get_post(session: AsyncSession, post_id: uuid.UUID) -> Post | None:
    return await session.get(Post, post_id)


async def create_post(session: AsyncSession, author: User, data: PostCreate) -> Post:
    post = Post(author_id=author.id, **data.model_dump())
    session.add(post)
    await session.flush()
    await session.refresh(post)
    return post


async def update_post(session: AsyncSession, post: Post, data: PostUpdate) -> Post:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(post, field, value)
    await session.flush()
    await session.refresh(post)
    return post


async def delete_post(session: AsyncSession, post: Post) -> None:
    await session.delete(post)
    await session.flush()
