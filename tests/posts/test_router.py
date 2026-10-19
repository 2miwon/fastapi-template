import uuid

from httpx import AsyncClient

from tests.conftest import register_and_login


async def test_post_crud(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resp = await client.post(
        "/posts", json={"title": "Hello", "content": "World"}, headers=auth_headers
    )
    assert resp.status_code == 201
    post_id = resp.json()["id"]

    resp = await client.get(f"/posts/{post_id}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Hello"

    resp = await client.patch(f"/posts/{post_id}", json={"title": "Edited"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["title"] == "Edited"
    assert resp.json()["content"] == "World"

    resp = await client.get("/posts")
    assert resp.json()["total"] == 1

    resp = await client.delete(f"/posts/{post_id}", headers=auth_headers)
    assert resp.status_code == 204
    assert (await client.get(f"/posts/{post_id}")).status_code == 404


async def test_post_not_found(client: AsyncClient) -> None:
    assert (await client.get(f"/posts/{uuid.uuid4()}")).status_code == 404


async def test_cannot_edit_others_post(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resp = await client.post("/posts", json={"title": "Mine"}, headers=auth_headers)
    post_id = resp.json()["id"]

    other_token = await register_and_login(client, "mallory@example.com")
    resp = await client.patch(
        f"/posts/{post_id}",
        json={"title": "Hacked"},
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert resp.status_code == 403


async def test_pagination_bounds(client: AsyncClient) -> None:
    assert (await client.get("/posts", params={"limit": 0})).status_code == 422
    assert (await client.get("/posts", params={"limit": 101})).status_code == 422
