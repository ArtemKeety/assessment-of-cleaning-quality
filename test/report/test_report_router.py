import pytest
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport

from database import DataBase
from internal.midleware import user_identy
from internal.service import ReportService
from internal.shemas import Report, ReportPath

from internal.router.report import router as report_router  # <-- поправь импорт под свой путь


def _get_route(app: FastAPI, path: str, method: str):
    method = method.upper()
    for r in app.routes:
        if getattr(r, "path", None) == path and method in getattr(r, "methods", set()):
            return r
    raise AssertionError(f"Route {method} {path} not found")


def _override_dep_by_index(app: FastAPI, path: str, method: str, index: int, override_callable):
    """
    Подменяем зависимость Depends(...) у endpoint-а по индексу в dependant.dependencies.
    """
    route = _get_route(app, path, method)
    dependant = route.dependant
    deps = dependant.dependencies
    assert len(deps) > index, f"Only {len(deps)} dependencies, index={index} is out of range"
    dep_call = deps[index].call
    app.dependency_overrides[dep_call] = override_callable
    return dep_call


def _override_all_simple_deps(app: FastAPI):
    """
    Общие overrides: conn + user_identy.
    """
    async def override_db_conn():
        return object()

    async def override_user_identy():
        return {"session": "sess-123", "user_id": 42}

    app.dependency_overrides[DataBase.from_request_conn] = override_db_conn
    app.dependency_overrides[user_identy] = override_user_identy


@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(report_router)

    _override_all_simple_deps(app)

    # ---- /report/add ----
    # endpoint:
    # flat_id: Body()
    # photos: Depends(ValidateFiles())
    # conn: Depends(DataBase.from_request_conn)
    # + dependencies=[Depends(CustomRateLimit(...))] (в декораторе)

    async def override_photos():
        return []  # список UploadFile; пустого хватает для тестов, т.к. сервис замокан

    async def override_rate_limit():
        # dependency в decorator dependencies=[...]
        return {"user_id": 42}

    # Тут есть нюанс: в route.dependant.dependencies будут и "параметровые" зависимости
    # (photos/conn) и "декораторные" dependencies=[...].
    #
    # Чтобы не гадать индекс, мы подменим "photos" перебором: найдём dependency,
    # у которой dependant.name == "photos". Но чтобы не усложнять, можно индексом —
    # чаще всего photos идёт первой среди Depends-параметров.
    #
    # Надёжный вариант: ищем по name.

    route_add = _get_route(app, "/report/add", "POST")
    deps = route_add.dependant.dependencies

    # подменяем ValidateFiles() (photos)
    for d in deps:
        if d.name == "photos":
            app.dependency_overrides[d.call] = override_photos
            break
    else:
        raise AssertionError("Dependency for 'photos' not found in /report/add")

    # подменяем CustomRateLimit(...) (decorator dependency)
    # У него name обычно None, поэтому ищем по call type/str сложно.
    # Сделаем проще: найдём dependency, которая НЕ conn и НЕ photos и НЕ user_identy
    # и подменим её. Обычно она одна.
    decorator_deps = [
        d for d in deps
        if d.name not in ("photos", "conn")
        and d.call not in (DataBase.from_request_conn, user_identy)
    ]
    # Часто decorator dependency будет ровно 1
    if len(decorator_deps) == 1:
        app.dependency_overrides[decorator_deps[0].call] = override_rate_limit
    else:
        # fallback: ничего не делаем, если лимитер не требует контекста
        # но лучше явно видеть проблему
        raise AssertionError(f"Unexpected decorator dependencies count: {len(decorator_deps)}")

    return app


# ---------------- tests ----------------

@pytest.mark.asyncio
async def test_add_report_calls_service_and_returns_report(monkeypatch, app):
    async def mock_add(flat_id, photos, conn):
        assert flat_id == 7
        assert isinstance(photos, list)
        return Report(id=1, flat_id=7)  # <-- подстрой поля Report если нужно

    monkeypatch.setattr(ReportService, "add", mock_add)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # flat_id: int = Body() -> отправляем JSON-число
        resp = await ac.post("/report/add", json=7)

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["flat_id"] == 7


@pytest.mark.asyncio
async def test_reports_returns_all_user_reports(monkeypatch, app):
    async def mock_get_reports(user_id, conn):
        assert user_id == 42
        return [Report(id=1, flat_id=1), Report(id=2, flat_id=2)]  # подстрой поля

    monkeypatch.setattr(ReportService, "get_reports", mock_get_reports)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/report/all")

    assert resp.status_code == 200, resp.text
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 2


@pytest.mark.asyncio
async def test_get_reports_by_flat_calls_service(monkeypatch, app):
    async def mock_get_an_flat(flat_id, conn):
        assert flat_id == 10
        return [Report(id=5, flat_id=10)]

    monkeypatch.setattr(ReportService, "get_an_flat", mock_get_an_flat)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/report/flat/10")

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data[0]["flat_id"] == 10


@pytest.mark.asyncio
async def test_current_report_returns_report_paths(monkeypatch, app):
    async def mock_get_current(report_id, conn):
        assert report_id == 99
        return [ReportPath(id=1, path="a.jpg"), ReportPath(id=2, path="b.jpg")]  # подстрой поля

    monkeypatch.setattr(ReportService, "get_current", mock_get_current)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/report/99")

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data[0]["path"] == "a.jpg"


@pytest.mark.asyncio
async def test_delete_report_calls_service(monkeypatch, app):
    async def mock_delete_report(report_id, conn):
        assert report_id == 77
        return 77

    monkeypatch.setattr(ReportService, "delete_report", mock_delete_report)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.delete("/report/77")

    assert resp.status_code == 200, resp.text
    assert resp.json() == 77
