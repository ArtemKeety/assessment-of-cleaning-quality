import asyncio
from fastapi_babel import _
from datetime import datetime
from zoneinfo import ZoneInfo
from tasks import request_from_ai
from dataclasses import dataclass
from fastapi import UploadFile, Request
from configuration import RAW_REPORT_FILE_PATH
from internal.midleware import CustomHTTPException
from internal.repository import Transaction, IRepository
from internal.shemas import Report, ReportPath, Pagination
from utils import download_files, TaskCondition, get_status



@dataclass(slots=True, frozen=True, init=True)
class ReportService:
    repository: IRepository

    async def add(self, flat_id: int, dirty_photos: list[UploadFile]) -> Report:

        async with Transaction(self.repository) as repo:

            clear_photos = await repo.Flat.get_id(flat_id)

            if len(clear_photos) != len(dirty_photos):
                raise CustomHTTPException(status_code=400, detail=_("Not equal count photos"))

            task: asyncio.Task = asyncio.create_task(download_files(dirty_photos, RAW_REPORT_FILE_PATH))

            time = datetime.now().astimezone(ZoneInfo("UTC")).replace(tzinfo=None)

            report_id = await repo.Report.add_report_place(flat_id, dirty_photos[0].filename, time)

            await repo.Report.add_report_photo_raw(
                    report_id=report_id,
                    info="Нейросесть обрабатывает запрос, подождите....",
                    photo="default.gif",
                    count=len(dirty_photos),
            )

            await task

        photos = [(dirty_obj.filename, clear_obj.path) for dirty_obj, clear_obj in zip(dirty_photos, clear_photos)]

        await asyncio.to_thread(
            request_from_ai.apply_async,
            (report_id, tuple(photos)),
            task_id=str(report_id)
        )

        return Report(id=report_id, flat_id=flat_id, preview=dirty_photos[0].filename, date=time)


    async def get_reports(self, user_id: int, pages: Pagination) -> list[Report]:
        return await self.repository.Report.get_reports(user_id, pages)


    async def get_an_flat(self, flat_id: int, pages: Pagination) -> list[Report]:
        return await self.repository.Report.get_an_flat(flat_id, pages)


    async def get_current(self, report_id: int) -> list[ReportPath]:
        return await self.repository.Report.get_current(report_id)


    async def delete_report(self, report_id: int) -> None:
        return await self.repository.Report.del_report(report_id)


    @staticmethod
    async def task(report_id: int, request: Request):

        while not await request.is_disconnected():

            state, meta = await asyncio.to_thread(get_status, str(report_id))

            conditions: tuple[bool, ...] = (
                state == TaskCondition.success or state == TaskCondition.failure,
                meta is None,
            )

            if any(conditions): break

            step, count = meta.get("step", 0), meta.get("count", 1)

            yield f"{(step / count) * 100:.2f}\n"

            await asyncio.sleep(1)

        yield "end\n"