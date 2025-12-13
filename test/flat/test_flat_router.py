import pytest
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport

import asyncpg

from database import DataBase
from internal.midleware import user_identy
from internal.service import FlatService
from internal.shemas import Flat, FullFlat

# твой router
from internal.router.flat import router as flat_router  # поправь импорт под свой путь


def _override_dep_in_route(app: FastAPI, path: str, method: str, index: int, override_callable):
    """
    Находит зависимость Depends(...) у endpoint-а по (path, method) и заменяет её через dependency_overrides.
    index — номер зависимости среди dependant.dependencies (обычно 0/1).
    """
    # ищем маршрут
    route = None
    for r in app.routes:
        if getattr(r, "path", None) == path and method.upper() in getattr(r, "methods", set()):
            route = r
            break
    assert route is not None, f"Route {method} {path} not found"

    dependant = getattr(route, "dependant", None)
    assert dependant is not None, "Route has no dependant"

    deps = dependant.dependencies
    assert len(deps) > index, f"Route has only {len(deps)} dependencies, index={index} is out of range"

    dep_call = deps[index].call  # вот тот самый объект/функция, который FastAPI будет вызывать
    app.dependency_overrides[dep_call] = override_callable
    return dep_call


@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(flat_router)

    async def override_db_conn():
        return object()

    async def override_user_identy():
        return {"session": "sess-123", "user_id": 42}

    app.dependency_overrides[DataBase.from_request_conn] = override_db_conn
    app.dependency_overrides[user_identy] = override_user_identy

    # --- ВАЖНО ---
    # В /flat/add у тебя две "нестандартные" зависимости:
    # photos: Depends(ValidateFiles())
    # user_data: Depends(CustomRateLimit(...))
    #
    # Мы достаем их из маршрута и override-им "на месте".

    async def override_photos():
        return []  # список UploadFile; для сервиса нам достаточно пустого списка

    async def override_user_data():
        return {"user_id": 42}

    # Порядок зависимостей в dependant.dependencies чаще всего соответствует порядку параметров с Depends.
    # В твоём add_flat: photos (Depends), user_data (Depends), conn (Depends).
    # Но conn мы уже override-им по DataBase.from_request_conn, так что интересуют первые две.
    _override_dep_in_route(app, "/flat/add", "POST", 0, override_photos)
    _override_dep_in_route(app, "/flat/add", "POST", 1, override_user_data)

    return app


@pytest.mark.asyncio
async def test_add_flat_returns_flat_and_calls_service(monkeypatch, app):
    async def mock_add(name, user_id, photos, conn):
        assert name == "My flat"
        assert user_id == 42
        assert isinstance(photos, list)
        return Flat(id=1, name="My flat")  # подстрой поля Flat если нужно

    monkeypatch.setattr(FlatService, "add", mock_add)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # name: str = Body() -> тело запроса просто JSON-строка
        resp = await ac.post("/flat/add", json="My flat")

    assert resp.status_code == 200, resp.text
    assert resp.json()["name"] == "My flat"


@pytest.mark.asyncio
async def test_get_flats_returns_list(monkeypatch, app):
    async def mock_all(user_id, conn):
        assert user_id == 42
        return [Flat(id=1, name="A"), Flat(id=2, name="B")]

    monkeypatch.setattr(FlatService, "all", mock_all)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/flat/all")

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 2


@pytest.mark.asyncio
async def test_get_flat_by_id_returns_fullflat_list(monkeypatch, app):
    async def mock_get_id(flat_id, conn):
        assert flat_id == 10
        return [FullFlat(id=10, name="A")]  # подстрой под поля FullFlat

    monkeypatch.setattr(FlatService, "get_id", mock_get_id)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/flat/10")

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data[0]["id"] == 10


@pytest.mark.asyncio
async def test_delete_flat_calls_service(monkeypatch, app):
    async def mock_delete(flat_id, conn):
        assert flat_id == 10
        return 10

    monkeypatch.setattr(FlatService, "delete", mock_delete)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.delete("/flat/10")

    assert resp.status_code == 200, resp.text
    assert resp.json() == 10
