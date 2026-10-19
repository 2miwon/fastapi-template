from collections.abc import AsyncIterator
from datetime import datetime
from typing import Annotated

from fastapi import Depends
from sqlalchemy import DateTime, MetaData, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.config import settings
from src.constants import DB_NAMING_CONVENTION

DATABASE_URL = str(settings.DATABASE_URL)

_engine_kwargs: dict[str, object] = {"pool_pre_ping": settings.DATABASE_POOL_PRE_PING}
if not DATABASE_URL.startswith("sqlite"):
    _engine_kwargs |= {
        "pool_size": settings.DATABASE_POOL_SIZE,
        "pool_recycle": settings.DATABASE_POOL_TTL,
    }

engine = create_async_engine(DATABASE_URL, **_engine_kwargs)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=DB_NAMING_CONVENTION)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )


async def get_db_session() -> AsyncIterator[AsyncSession]:
    """Unit of work: one session + one transaction per request.

    Commits when the route returns, rolls back if it raises. Services only `flush()`.
    """
    async with async_session_maker() as session, session.begin():
        yield session


# scope="function" makes the commit run *before* the response is sent, so a failed
# commit becomes an error response instead of a silent 200 (default scope tears down after).
DbSession = Annotated[AsyncSession, Depends(get_db_session, scope="function")]
