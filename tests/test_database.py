from httpx import AsyncClient
from sqlalchemy import func, select

from src.auth.models import User
from src.database import DbSession
from src.exceptions import BadRequest
from src.main import app


async def test_request_rolls_back_on_error(client: AsyncClient) -> None:
    """Anything flushed during a request that raises must not be committed."""

    async def create_then_fail(session: DbSession) -> None:
        session.add(User(email="ghost@example.com", hashed_password="x"))
        await session.flush()
        raise BadRequest()

    app.add_api_route("/_test/rollback", create_then_fail, methods=["POST"])
    try:
        resp = await client.post("/_test/rollback")
    finally:
        app.router.routes.pop()
    assert resp.status_code == 400

    async def count_users(session: DbSession) -> int:
        return await session.scalar(select(func.count()).select_from(User)) or 0

    app.add_api_route("/_test/count", count_users, methods=["GET"])
    try:
        assert (await client.get("/_test/count")).json() == 0
    finally:
        app.router.routes.pop()
