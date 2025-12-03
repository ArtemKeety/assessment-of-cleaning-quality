import os
import asyncio
import asyncpg
from datetime import datetime
from zoneinfo import ZoneInfo
from utils import download_files
from repo import ReportRepo, FlatRepo
from midleware import CustomHTTPException
from shemas import FullFlat, Report, ReportPath
from fastapi import UploadFile, BackgroundTasks
from tasks import request_from_ai, request_from_aiV2
from configuration import RAW_REPORT_FILE_PATH, FLAT_FILE_PATH



class ReportService:

    @staticmethod
    async def add(flat_id: int, photos: list[UploadFile], conn: asyncpg.Connection) -> int:

        db_photo = await FlatRepo.get_id(flat_id, conn)

        clear_photos: list[str] = [obj.path for obj in db_photo]

        if len(clear_photos) != len(photos):
            raise CustomHTTPException(status_code=400, detail="not equal count photos")

        task_1: asyncio.Task = asyncio.create_task(download_files(photos, RAW_REPORT_FILE_PATH))

        time = datetime.now().astimezone(ZoneInfo("UTC")).replace(tzinfo=None)

        report_id = await ReportRepo.add_report_place(flat_id, photos[0].filename, time, conn)

        dirty_photos = [obj.filename for obj in photos]

        if not await ReportRepo.add_report_photo_raw(
                report_id=report_id,
                info="Нейросесть обрабатывает запрос, подождите....",
                photo="default.gif",
                count=len(photos),
                conn=conn,
        ):
            task_1.cancel()
            await ReportRepo.del_report(report_id, conn)
            raise CustomHTTPException(status_code=501, detail="Error in adding report")

        await task_1

        request_from_ai.delay(report_id, dirty_photos, clear_photos)

        return report_id

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
    async def delete_report(report_id: int, conn: asyncpg.Connection) -> None:
        return await ReportRepo.del_report(report_id, conn)