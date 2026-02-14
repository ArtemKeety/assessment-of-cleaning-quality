import asyncpg
from fastapi_babel import _
from datetime import datetime
from dataclasses import dataclass
from internal.shemas import Report, ReportPath
from internal.midleware import CustomHTTPException

@dataclass(slots=True, frozen=True, init=True)
class ReportRepo:
    conn: asyncpg.Connection


    async def add_report_place(self, flat_id: int, path: str, date: datetime)-> int:
        if res := await self.conn.fetchval(
            "INSERT INTO report (flat_id, preview, date) VALUES ($1, $2, $3) RETURNING id",
            flat_id, path, date,
        ):
            return res
        raise CustomHTTPException(status_code=501, detail=_("Error adding report"))


    async def add_report_photo_raw(self, report_id: int, info: str, photo: str, count: int) -> None:
        req = await self.conn.prepare("insert into report_part (report_id, info, path) values ($1, $2, $3)")
        for _ in range(count):
            await req.fetchval(report_id, info, photo)


    async def del_report(self, report_id: int) -> int:
        if res := await self.conn.fetchval(
            "DELETE FROM report WHERE id = $1 RETURNING id",
            report_id,
        ):
            return res
        raise CustomHTTPException(status_code=404, detail=_("Error deleting report"))


    async def get_reports(self, user_id:int) -> list[Report]:
        if res := await self.conn.fetch(
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



    async def get_an_flat(self, flat_id: int) -> list[Report]:
        if res := await self.conn.fetch(
          "select * from report where flat_id = $1",
            flat_id,
        ):
            return [Report(**obj) for obj in res]
        raise CustomHTTPException(status_code=404, detail=_("Not found report"))


    async def get_current(self, report_id: int) -> list[ReportPath]:
        if res := await self.conn.fetch(
            "select * from report_part where report_id = $1",
            report_id,
        ):
            return [ReportPath(**obj) for obj in res]
        raise CustomHTTPException(status_code=404, detail=_("Not found report"))

