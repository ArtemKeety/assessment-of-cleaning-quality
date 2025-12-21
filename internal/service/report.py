import asyncio
import asyncpg
from fastapi_babel import _
from datetime import datetime
from zoneinfo import ZoneInfo
from tasks import request_from_ai
from celery.result import AsyncResult
from fastapi import UploadFile, Request
from configuration import RAW_REPORT_FILE_PATH
from internal.shemas import Report, ReportPath
from internal.repo import ReportRepo, FlatRepo
from utils import download_files, TaskCondition
from internal.midleware import CustomHTTPException



class ReportService:

    @staticmethod
    async def add(flat_id: int, photos: list[UploadFile], conn: asyncpg.Connection) -> Report:

        async with conn.transaction():
            db_photo = await FlatRepo.get_id(flat_id, conn)

            clear_photos: list[str] = [obj.path for obj in db_photo]

            if len(clear_photos) != len(photos):
                raise CustomHTTPException(status_code=400, detail=_("Not equal count photos"))

            task: asyncio.Task = asyncio.create_task(download_files(photos, RAW_REPORT_FILE_PATH))

            time = datetime.now().astimezone(ZoneInfo("UTC")).replace(tzinfo=None)

            report_id = await ReportRepo.add_report_place(flat_id, photos[0].filename, time, conn)

            dirty_photos = [obj.filename for obj in photos]

            await ReportRepo.add_report_photo_raw(
                    report_id=report_id,
                    info="Нейросесть обрабатывает запрос, подождите....",
                    photo="default.gif",
                    count=len(photos),
                    conn=conn,
            )

        await task

        request_from_ai.apply_async(args=(report_id, dirty_photos, clear_photos),  task_id=str(report_id))

        return Report(id=report_id, flat_id=flat_id, preview=photos[0].filename, date=time)

    @staticmethod
    async def get_reports(user_id: int, conn: asyncpg.Connection) -> list[Report]:
        return await ReportRepo.get_reports(user_id, conn)

    @staticmethod
    async def get_an_flat(flat_id: int, conn: asyncpg.Connection) -> list[Report]:
        return await ReportRepo.get_an_flat(flat_id, conn)

    @staticmethod
    async def get_current(report_id: int, conn: asyncpg.Connection) -> list[ReportPath]:
        return await ReportRepo.get_current(report_id, conn)

    @staticmethod
    async def delete_report(report_id: int, conn: asyncpg.Connection) -> int:
        return await ReportRepo.del_report(report_id, conn)

    @staticmethod
    async def task(report_id: int, request: Request):

        while True:

            if await request.is_disconnected(): break

            if not (result := AsyncResult(str(report_id))): break

            condition = result.state == TaskCondition.success or result.state == TaskCondition.failure

            if condition: break

            meta: dict = result.info

            if meta is None: raise CustomHTTPException(status_code=500, detail=_("An unexpected error has occurred"))

            yield f"{(meta.get("step", 0) * (meta.get("count", 1) / 100))}"

            await asyncio.sleep(1)

        yield "100"