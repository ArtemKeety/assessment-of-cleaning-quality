import pytest
from datetime import datetime

from internal.midleware import CustomHTTPException
from internal.shemas import Report, ReportPath
from internal.repo.report import ReportRepo  # <-- поправь путь


# ---------- helpers ----------

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
    # monkeypatch "_" в модуле, где объявлен ReportRepo
    import internal.repo.report as report_repo_module  # <-- поправь под свой модуль
    monkeypatch.setattr(report_repo_module, "_", lambda s: s)


# ---------- add_report_place ----------

@pytest.mark.asyncio
async def test_add_report_place_returns_id_and_calls_fetchval():
    conn = FakeConn(fetchval_result=101)
    dt = datetime(2025, 12, 13, 12, 0, 0)

    report_id = await ReportRepo.add_report_place(flat_id=7, path="prev.jpg", date=dt, conn=conn)

    assert report_id == 101
    assert len(conn.fetchval_calls) == 1

    query, args = conn.fetchval_calls[0]
    assert "INSERT INTO report" in query
    assert args == (7, "prev.jpg", dt)


@pytest.mark.asyncio
async def test_add_report_place_raises_when_no_id_returned():
    conn = FakeConn(fetchval_result=None)
    dt = datetime(2025, 12, 13, 12, 0, 0)

    with pytest.raises(CustomHTTPException) as exc:
        await ReportRepo.add_report_place(flat_id=7, path="prev.jpg", date=dt, conn=conn)

    err = exc.value
    assert getattr(err, "status_code", None) == 501
    assert "Error adding report" in str(getattr(err, "detail", err))


# ---------- add_report_photo_raw ----------

@pytest.mark.asyncio
async def test_add_report_photo_raw_prepares_once_and_inserts_count_times():
    prepared = FakePrepared()
    conn = FakeConn(prepared=prepared)

    await ReportRepo.add_report_photo_raw(
        report_id=10,
        info="kitchen",
        photo="a.jpg",
        count=3,
        conn=conn,
    )

    assert len(conn.prepare_calls) == 1
    assert "insert into report_part" in conn.prepare_calls[0].lower()

    assert prepared.calls == [
        (10, "kitchen", "a.jpg"),
        (10, "kitchen", "a.jpg"),
        (10, "kitchen", "a.jpg"),
    ]


@pytest.mark.asyncio
async def test_add_report_photo_raw_with_zero_count_does_not_insert():
    prepared = FakePrepared()
    conn = FakeConn(prepared=prepared)

    await ReportRepo.add_report_photo_raw(
        report_id=10,
        info="kitchen",
        photo="a.jpg",
        count=0,
        conn=conn,
    )

    assert len(conn.prepare_calls) == 1  # prepare всё равно вызывается в текущей реализации
    assert prepared.calls == []


# ---------- del_report ----------

@pytest.mark.asyncio
async def test_del_report_returns_id_when_deleted():
    conn = FakeConn(fetchval_result=77)

    res = await ReportRepo.del_report(report_id=77, conn=conn)

    assert res == 77
    assert len(conn.fetchval_calls) == 1
    query, args = conn.fetchval_calls[0]
    assert "DELETE FROM report" in query
    assert args == (77,)


@pytest.mark.asyncio
async def test_del_report_raises_when_not_found():
    conn = FakeConn(fetchval_result=None)

    with pytest.raises(CustomHTTPException) as exc:
        await ReportRepo.del_report(report_id=999, conn=conn)

    err = exc.value
    assert getattr(err, "status_code", None) == 404
    assert "Error deleting report" in str(getattr(err, "detail", err))


# ---------- get_reports ----------

@pytest.mark.asyncio
async def test_get_reports_returns_list_when_rows_exist():
    dt = datetime(2025, 12, 13, 12, 0, 0)

    conn = FakeConn(fetch_result=[
        {"id": 1, "flat_id": 10, "preview": "p1.jpg", "date": dt},
        {"id": 2, "flat_id": 11, "preview": "p2.jpg", "date": dt},
    ])

    res = await ReportRepo.get_reports(user_id=42, conn=conn)

    assert isinstance(res, list)
    assert len(res) == 2
    assert isinstance(res[0], Report)
    assert res[0].id == 1
    assert res[0].flat_id == 10

    assert len(conn.fetch_calls) == 1
    query, args = conn.fetch_calls[0]
    assert "from report" in query.lower()
    assert args == (42,)


@pytest.mark.asyncio
async def test_get_reports_returns_empty_list_when_no_rows():
    conn = FakeConn(fetch_result=[])

    res = await ReportRepo.get_reports(user_id=42, conn=conn)
    assert res == []


# ---------- get_an_flat ----------

@pytest.mark.asyncio
async def test_get_an_flat_returns_list_when_rows_exist():
    dt = datetime(2025, 12, 13, 12, 0, 0)

    conn = FakeConn(fetch_result=[
        {"id": 3, "flat_id": 10, "preview": "p3.jpg", "date": dt},
    ])

    res = await ReportRepo.get_an_flat(flat_id=10, conn=conn)

    assert len(res) == 1
    assert isinstance(res[0], Report)
    assert res[0].flat_id == 10

    assert len(conn.fetch_calls) == 1
    query, args = conn.fetch_calls[0]
    assert "select * from report" in query.lower()
    assert args == (10,)


@pytest.mark.asyncio
async def test_get_an_flat_raises_when_no_rows():
    conn = FakeConn(fetch_result=[])

    with pytest.raises(CustomHTTPException) as exc:
        await ReportRepo.get_an_flat(flat_id=999, conn=conn)

    err = exc.value
    assert getattr(err, "status_code", None) == 404
    assert "Not found report" in str(getattr(err, "detail", err))


# ---------- get_current ----------

@pytest.mark.asyncio
async def test_get_current_returns_list_of_report_paths():
    conn = FakeConn(fetch_result=[
        {"id": 1, "report_id": 10, "info": "kitchen", "path": "a.jpg"},
        {"id": 2, "report_id": 10, "info": "bath", "path": "b.jpg"},
    ])

    res = await ReportRepo.get_current(report_id=10, conn=conn)

    assert isinstance(res, list)
    assert len(res) == 2
    assert isinstance(res[0], ReportPath)
    assert res[0].path == "a.jpg"

    assert len(conn.fetch_calls) == 1
    query, args = conn.fetch_calls[0]
    assert "from report_part" in query.lower()
    assert args == (10,)


@pytest.mark.asyncio
async def test_get_current_raises_when_no_rows():
    conn = FakeConn(fetch_result=[])

    with pytest.raises(CustomHTTPException) as exc:
        await ReportRepo.get_current(report_id=999, conn=conn)

    err = exc.value
    assert getattr(err, "status_code", None) == 404
    assert "Not found report" in str(getattr(err, "detail", err))
