from httpx import AsyncClient


async def test_healthcheck(client: AsyncClient) -> None:
    resp = await client.get("/healthcheck")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
