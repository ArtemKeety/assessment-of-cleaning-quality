import asyncpg
from fastapi_babel import _
from datetime import datetime
from customlogger import LOGGER
from shemas import Report, ReportPath
from midleware import CustomHTTPException



class ReportRepo:

    @staticmethod
    async def add_report_place(flat_id: int, path: str, date: datetime, conn: asyncpg.Connection)-> int:
        if res := await conn.fetchval(
            "INSERT INTO report (flat_id, preview, date) VALUES ($1, $2, $3) RETURNING id",
            flat_id, path, date,
        ):
            return res
        raise CustomHTTPException(status_code=501, detail=_("Error adding report"))

    @staticmethod
    async def add_report_photo_raw(report_id: int, info: str, photo: str, count: int, conn: asyncpg.Connection) -> bool:
        req = await conn.prepare("insert into report_part (report_id, info, path) values ($1, $2, $3)")
        for _ in range(count):
            await req.fetchval(report_id, info, photo)

    @staticmethod
    async def del_report(report_id: int, conn: asyncpg.Connection) -> int:
        if res := await conn.fetchval(
            "DELETE FROM report WHERE id = $1 RETURNING id",
            report_id,
        ):
            return res
        raise CustomHTTPException(status_code=404, detail=_("Error deleting report"))

    @staticmethod
    async def get_reports(user_id:int, conn: asyncpg.Connection) -> list[Report]:
        if res := await conn.fetch(
            """
                select r.id, r.flat_id, r.preview, r.date
                from report r
                join flat f on f.id = r.flat_id
                where f.user_id = $1
            """,
            user_id,
        ):
            return [Report(**obj) for obj in res]
        return []

    @staticmethod
    async def get_an_flat(flat_id: int, conn: asyncpg.Connection) -> list[Report]:
        if res := await conn.fetch(
          "select * from report where flat_id = $1",
            flat_id,
        ):
            return [Report(**obj) for obj in res]
        raise CustomHTTPException(status_code=404, detail=_("Not found report"))

    @staticmethod
    async def get_current(report_id: int, conn: asyncpg.Connection) -> list[ReportPath]:
        if res := await conn.fetch(
            "select * from report_part where report_id = $1",
            report_id,
        ):
            return [ReportPath(**obj) for obj in res]
        raise CustomHTTPException(status_code=404, detail=_("Not found report"))

