import os

# Must be set before `src` is imported so settings pick them up.
os.environ["ENVIRONMENT"] = "TESTING"
os.environ["DATABASE_URL"] = os.getenv("TEST_DATABASE_URL", "sqlite+aiosqlite://")
os.environ.setdefault("JWT_SECRET", "test-secret-key-that-is-long-enough-for-hs256")

from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from src.database import get_db_session
from src.main import app
from src.models import Base


@pytest.fixture(scope="session")
async def engine() -> AsyncIterator[AsyncEngine]:
    url = os.environ["DATABASE_URL"]
    kwargs = {"poolclass": StaticPool} if url.startswith("sqlite") else {}
    engine = create_async_engine(url, **kwargs)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def session_maker(engine: AsyncEngine) -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    yield async_sessionmaker(engine, expire_on_commit=False, autoflush=False)
    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())


@pytest.fixture
async def client(session_maker: async_sessionmaker[AsyncSession]) -> AsyncIterator[AsyncClient]:
    async def override_session() -> AsyncIterator[AsyncSession]:
        async with session_maker() as session, session.begin():
            yield session

    app.dependency_overrides[get_db_session] = override_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


async def register_and_login(client: AsyncClient, email: str, password: str = "password123") -> str:
    resp = await client.post("/auth/users", json={"email": email, "password": password})
    assert resp.status_code == 201, resp.text
    resp = await client.post("/auth/token", data={"username": email, "password": password})
    assert resp.status_code == 200, resp.text
    return str(resp.json()["access_token"])


@pytest.fixture
async def auth_headers(client: AsyncClient) -> dict[str, str]:
    token = await register_and_login(client, "alice@example.com")
    return {"Authorization": f"Bearer {token}"}
