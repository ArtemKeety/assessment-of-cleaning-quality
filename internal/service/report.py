import asyncio
import asyncpg
from fastapi_babel import _
from decimal import Decimal
from datetime import datetime
from zoneinfo import ZoneInfo
from tasks import request_from_ai
from fastapi import UploadFile, Request
from configuration import RAW_REPORT_FILE_PATH
from internal.shemas import Report, ReportPath
from internal.repo import ReportRepo, FlatRepo
from internal.midleware import CustomHTTPException
from utils import download_files, TaskCondition, get_status




class ReportService:

    @staticmethod
    async def add(flat_id: int, dirty_photos: list[UploadFile], conn: asyncpg.Connection) -> Report:

        async with conn.transaction():
            clear_photos = await FlatRepo.get_id(flat_id, conn)

            if len(clear_photos) != len(dirty_photos):
                raise CustomHTTPException(status_code=400, detail=_("Not equal count photos"))

            task: asyncio.Task = asyncio.create_task(download_files(dirty_photos, RAW_REPORT_FILE_PATH))

            time = datetime.now().astimezone(ZoneInfo("UTC")).replace(tzinfo=None)

            report_id = await ReportRepo.add_report_place(flat_id, dirty_photos[0].filename, time, conn)

            await ReportRepo.add_report_photo_raw(
                    report_id=report_id,
                    info="Нейросесть обрабатывает запрос, подождите....",
                    photo="default.gif",
                    count=len(dirty_photos),
                    conn=conn,
            )

            await task

        await asyncio.to_thread(
            request_from_ai.apply_async,
            (report_id, [obj.filename for obj in dirty_photos], [obj.path for obj in clear_photos]),
            task_id=str(report_id)
        )

        return Report(id=report_id, flat_id=flat_id, preview=dirty_photos[0].filename, date=time)

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

        while not await request.is_disconnected():

            state, meta = await asyncio.to_thread(get_status, str(report_id))

            conditions = (
                state == TaskCondition.success or state == TaskCondition.failure,
                meta is None,
            )

            if any(conditions): break

            step: Decimal = Decimal(meta.get("step", 0))
            count: Decimal = Decimal(meta.get("count", 1))
            percent: Decimal = step * (100 / count)

            yield f"{percent:.2f}\n"

            await asyncio.sleep(1)

        yield "end\n"