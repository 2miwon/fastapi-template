from httpx import AsyncClient


async def test_register(client: AsyncClient) -> None:
    resp = await client.post(
        "/auth/users", json={"email": "Bob@Example.com", "password": "password123"}
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "bob@example.com"
    assert "hashed_password" not in body


async def test_register_duplicate_email(client: AsyncClient) -> None:
    payload = {"email": "bob@example.com", "password": "password123"}
    assert (await client.post("/auth/users", json=payload)).status_code == 201
    resp = await client.post("/auth/users", json=payload)
    assert resp.status_code == 409


async def test_register_weak_password(client: AsyncClient) -> None:
    resp = await client.post(
        "/auth/users", json={"email": "bob@example.com", "password": "abcdefgh"}
    )
    assert resp.status_code == 422


async def test_login_wrong_password(client: AsyncClient) -> None:
    await client.post("/auth/users", json={"email": "bob@example.com", "password": "password123"})
    resp = await client.post(
        "/auth/token", data={"username": "bob@example.com", "password": "nope1234"}
    )
    assert resp.status_code == 401


async def test_me(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resp = await client.get("/auth/users/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "alice@example.com"


async def test_me_unauthenticated(client: AsyncClient) -> None:
    assert (await client.get("/auth/users/me")).status_code == 401
    resp = await client.get("/auth/users/me", headers={"Authorization": "Bearer garbage"})
    assert resp.status_code == 401
