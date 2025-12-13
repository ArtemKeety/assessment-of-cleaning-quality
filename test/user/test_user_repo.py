import pytest

from internal.repo.user import UserRepo  # поправь импорт под свой путь
from internal.shemas import UserLogin
from internal.midleware import CustomHTTPException


class FakeConn:
    def __init__(self, *, fetchrow_result=None, fetchval_result=None):
        self._fetchrow_result = fetchrow_result
        self._fetchval_result = fetchval_result
        self.fetchrow_calls = []
        self.fetchval_calls = []

    async def fetchrow(self, query, *args):
        self.fetchrow_calls.append((query, args))
        return self._fetchrow_result

    async def fetchval(self, query, *args):
        self.fetchval_calls.append((query, args))
        return self._fetchval_result


@pytest.mark.asyncio
async def test_get_user_returns_user_when_found(monkeypatch):
    # Заглушаем babel _ чтобы не зависеть от контекста
    import internal.repo.user as user_repo_module  # поправь под свой модуль
    monkeypatch.setattr(user_repo_module, "_", lambda s: s)

    conn = FakeConn(fetchrow_result={
        "id": 1,
        "login": "test",
        "password": "hashed",
        "is_active": True,
    })

    u = UserLogin(login="test", password="pass")
    res = await UserRepo.get_user(u, conn)

    assert res is not None
    assert res.id == 1
    assert res.login == "test"

    assert len(conn.fetchrow_calls) == 1
    query, args = conn.fetchrow_calls[0]
    assert "SELECT * FROM users" in query
    assert args == ("test",)


@pytest.mark.asyncio
async def test_get_user_returns_none_when_not_found(monkeypatch):
    import internal.repo.user as user_repo_module  # поправь под свой модуль
    monkeypatch.setattr(user_repo_module, "_", lambda s: s)

    conn = FakeConn(fetchrow_result=None)

    u = UserLogin(login="missing", password="pass")
    res = await UserRepo.get_user(u, conn)

    assert res is None
    assert len(conn.fetchrow_calls) == 1


@pytest.mark.asyncio
async def test_add_user_returns_new_id(monkeypatch):
    import internal.repo.user as user_repo_module  # поправь под свой модуль
    monkeypatch.setattr(user_repo_module, "_", lambda s: s)

    conn = FakeConn(fetchval_result=123)

    u = UserLogin(login="new", password="hashed")
    new_id = await UserRepo.add_user(u, conn)

    assert new_id == 123
    assert len(conn.fetchval_calls) == 1
    query, args = conn.fetchval_calls[0]
    assert "insert into users" in query.lower()
    assert args == ("new", "hashed")


@pytest.mark.asyncio
async def test_del_user_returns_id_when_updated(monkeypatch):
    import internal.repo.user as user_repo_module  # поправь под свой модуль
    monkeypatch.setattr(user_repo_module, "_", lambda s: s)

    conn = FakeConn(fetchval_result=42)

    res = await UserRepo.del_user(42, conn)
    assert res == 42

    assert len(conn.fetchval_calls) == 1
    query, args = conn.fetchval_calls[0]
    assert "update users" in query.lower()
    assert args == (False, 42)


@pytest.mark.asyncio
async def test_del_user_raises_custom_exception_when_not_updated(monkeypatch):
    import internal.repo.user as user_repo_module  # поправь под свой модуль
    monkeypatch.setattr(user_repo_module, "_", lambda s: s)

    conn = FakeConn(fetchval_result=None)

    with pytest.raises(CustomHTTPException) as exc:
        await UserRepo.del_user(999, conn)

    # если в CustomHTTPException есть status_code/detail — можно проверить так:
    err = exc.value
    assert getattr(err, "status_code", None) == 501
    assert "Error in deleting user" in str(getattr(err, "detail", err))
