import asyncio
import asyncpg
from fastapi_babel import _
from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi import UploadFile
from utils import download_files
from tasks import request_from_ai
from shemas import Report, ReportPath
from repo import ReportRepo, FlatRepo
from midleware import CustomHTTPException
from configuration import RAW_REPORT_FILE_PATH



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

        request_from_ai.delay(report_id, dirty_photos, clear_photos)

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