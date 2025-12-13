import pytest
from httpx import AsyncClient, ASGITransport

from internal.service import UserService
from internal.router import user_router
from internal.shemas import Session
from test.utils.conftest import TestAppFactory, FakeRedis
import fastapi_babel.helpers as babel_helpers


@pytest.fixture
def fake_redis():
    return FakeRedis()


@pytest.fixture
def app_factory(fake_redis):
    return TestAppFactory(routers=user_router, fake_redis=fake_redis)


@pytest.fixture
def app(app_factory):
    return app_factory.build()


@pytest.fixture(autouse=True)
def disable_babel_context(monkeypatch):
    monkeypatch.setattr(babel_helpers, "_", lambda s: s)


@pytest.mark.asyncio
async def test_sign_up_sets_cookie_and_returns_session(app, monkeypatch):
    async def mock_sign_up(r, agent, redis, conn):
        return Session(session="new-session-abc")

    monkeypatch.setattr(UserService, "sign_up", mock_sign_up)

    payload = {
        "login": "test@example.com",
        "password": "Qwerty123!",
        "confirm": "Qwerty123!",   # <-- добавили
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post("/user/sign-up", json=payload)

    assert resp.status_code == 200, resp.text
    assert resp.json()["session"] == "new-session-abc"

    set_cookie = resp.headers.get("set-cookie", "")
    assert "session=new-session-abc" in set_cookie



@pytest.mark.asyncio
async def test_sign_in_sets_cookie_and_returns_session(app, monkeypatch):
    async def mock_sign_in(u, agent, redis, conn):
        return Session(session="login-session-xyz")

    monkeypatch.setattr(UserService, "sign_in", mock_sign_in)

    payload = {
        "login": "test@example.com",   # <-- было email
        "password": "Qwerty123!",
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post("/user/sign-in", json=payload)

    assert resp.status_code == 200, resp.text
    assert resp.json()["session"] == "login-session-xyz"

    set_cookie = resp.headers.get("set-cookie", "")
    assert "session=login-session-xyz" in set_cookie


@pytest.mark.asyncio
async def test_logout_deletes_session_in_redis_and_deletes_cookie(app, fake_redis):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post("/user/logout")

    assert resp.status_code == 200
    assert resp.json() == {"message": "success"}

    assert "sess-123" in fake_redis.deleted_keys

    set_cookie = resp.headers.get("set-cookie", "")
    assert "session=" in set_cookie


@pytest.mark.asyncio
async def test_delete_user_deletes_session_and_calls_del_user(app, fake_redis, monkeypatch):
    # del_user вызывается без self
    async def mock_del_user(user_id, conn):
        assert user_id == 42
        return 42

    monkeypatch.setattr(UserService, "del_user", mock_del_user)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.delete("/user/delete")

    assert resp.status_code == 200, resp.text
    assert resp.json() == 42

    assert "sess-123" in fake_redis.deleted_keys

    set_cookie = resp.headers.get("set-cookie", "")
    assert "session=" in set_cookie


@pytest.mark.asyncio
async def test_check_auth_success(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/user/check-auth")

    assert resp.status_code == 200
    assert resp.json() == {"message": "success"}
