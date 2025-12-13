import pytest

from internal.midleware import CustomHTTPException
from internal.shemas import Flat, FullFlat

from internal.repo.flat import FlatRepo  # <-- поправь путь (пример)


# --------- helpers ---------

class FakeUploadFile:
    def __init__(self, filename: str):
        self.filename = filename


class FakePrepared:
    def __init__(self):
        self.calls = []

    async def fetchval(self, *args):
        self.calls.append(args)
        return True


class FakeConn:
    def __init__(self, *, fetchval_result=None, fetch_result=None, prepared=None):
        self._fetchval_result = fetchval_result
        self._fetch_result = fetch_result
        self._prepared = prepared or FakePrepared()

        self.fetchval_calls = []
        self.fetch_calls = []
        self.prepare_calls = []

    async def fetchval(self, query, *args):
        self.fetchval_calls.append((query, args))
        return self._fetchval_result

    async def fetch(self, query, *args):
        self.fetch_calls.append((query, args))
        return self._fetch_result

    async def prepare(self, query):
        self.prepare_calls.append(query)
        return self._prepared


@pytest.fixture(autouse=True)
def disable_babel(monkeypatch):
    # ВАЖНО: здесь monkeypatch-им "_" в модуле, где объявлен FlatRepo
    import internal.repo.flat as flat_repo_module  # <-- поправь под свой модуль
    monkeypatch.setattr(flat_repo_module, "_", lambda s: s)


# --------- tests: add_flat ---------

@pytest.mark.asyncio
async def test_add_flat_returns_id_and_calls_fetchval():
    conn = FakeConn(fetchval_result=123)
    preview = FakeUploadFile("preview.jpg")

    flat_id = await FlatRepo.add_flat("My flat", user_id=42, preview=preview, conn=conn)

    assert flat_id == 123
    assert len(conn.fetchval_calls) == 1

    query, args = conn.fetchval_calls[0]
    assert "INSERT INTO flat" in query
    assert args == ("My flat", 42, "preview.jpg")


@pytest.mark.asyncio
async def test_add_flat_raises_when_no_id_returned():
    conn = FakeConn(fetchval_result=None)
    preview = FakeUploadFile("preview.jpg")

    with pytest.raises(CustomHTTPException) as exc:
        await FlatRepo.add_flat("My flat", user_id=42, preview=preview, conn=conn)

    err = exc.value
    assert getattr(err, "status_code", None) == 501
    # detail может храниться по-разному — проверим через str
    assert "Error in adding flat" in str(getattr(err, "detail", err))


# --------- tests: add_flat_photo ---------

@pytest.mark.asyncio
async def test_add_flat_photo_prepares_and_inserts_each_photo():
    prepared = FakePrepared()
    conn = FakeConn(prepared=prepared)

    photos = [FakeUploadFile("1.jpg"), FakeUploadFile("2.jpg")]
    await FlatRepo.add_flat_photo(photos=photos, flat_id=10, conn=conn)

    assert len(conn.prepare_calls) == 1
    assert "INSERT INTO photo" in conn.prepare_calls[0]

    # проверяем, что на каждый файл был вызов fetchval(path, flat_id)
    assert prepared.calls == [("1.jpg", 10), ("2.jpg", 10)]


# --------- tests: delete ---------

@pytest.mark.asyncio
async def test_delete_returns_id_when_deleted():
    conn = FakeConn(fetchval_result=10)

    res = await FlatRepo.delete(flat_id=10, conn=conn)

    assert res == 10
    assert len(conn.fetchval_calls) == 1
    query, args = conn.fetchval_calls[0]
    assert "DELETE FROM flat" in query
    assert args == (10,)


@pytest.mark.asyncio
async def test_delete_raises_when_not_found():
    conn = FakeConn(fetchval_result=None)

    with pytest.raises(CustomHTTPException) as exc:
        await FlatRepo.delete(flat_id=999, conn=conn)

    err = exc.value
    assert getattr(err, "status_code", None) == 404
    assert "Error in deleting flat" in str(getattr(err, "detail", err))


# --------- tests: all ---------

@pytest.mark.asyncio
async def test_all_returns_list_of_flats():
    # Подстрой поля под твою модель Flat, если она требует больше полей
    conn = FakeConn(fetch_result=[
        {"id": 1, "name": "A", "preview": "a.jpg"},
        {"id": 2, "name": "B", "preview": "b.jpg"},
    ])

    res = await FlatRepo.all(user_id=42, conn=conn)

    assert isinstance(res, list)
    assert len(res) == 2
    assert isinstance(res[0], Flat)
    assert res[0].id == 1
    assert res[0].name == "A"

    assert len(conn.fetch_calls) == 1
    query, args = conn.fetch_calls[0]
    assert "SELECT id, name, preview FROM flat" in query
    assert args == (42,)


@pytest.mark.asyncio
async def test_all_returns_empty_list_when_no_rows():
    conn = FakeConn(fetch_result=[])

    res = await FlatRepo.all(user_id=42, conn=conn)

    assert res == []


# --------- tests: get_id ---------

@pytest.mark.asyncio
async def test_get_id_returns_list_of_fullflats():
    # Подстрой поля под твою модель FullFlat, если она требует больше полей
    conn = FakeConn(fetch_result=[
        {"id": 10, "path": "1.jpg"},
        {"id": 11, "path": "2.jpg"},
    ])

    res = await FlatRepo.get_id(flat_id=5, conn=conn)

    assert isinstance(res, list)
    assert len(res) == 2
    assert isinstance(res[0], FullFlat)
    assert res[0].id == 10
    assert res[0].path == "1.jpg"

    assert len(conn.fetch_calls) == 1
    query, args = conn.fetch_calls[0]
    assert "join photo" in query.lower()
    assert args == (5,)


@pytest.mark.asyncio
async def test_get_id_raises_when_no_rows():
    conn = FakeConn(fetch_result=[])

    with pytest.raises(CustomHTTPException) as exc:
        await FlatRepo.get_id(flat_id=999, conn=conn)

    err = exc.value
    assert getattr(err, "status_code", None) == 404
    assert "Not found flat full data" in str(getattr(err, "detail", err))


# --------- tests: count ---------

@pytest.mark.asyncio
async def test_count_returns_int_and_calls_fetchval():
    conn = FakeConn(fetchval_result=7)

    res = await FlatRepo.count(user_id=42, conn=conn)

    assert res == 7
    assert len(conn.fetchval_calls) == 1
    query, args = conn.fetchval_calls[0]
    assert "select count(*) from flat" in query.lower()
    assert args == (42,)
