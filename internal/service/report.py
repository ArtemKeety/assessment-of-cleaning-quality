import asyncio
from fastapi_babel import _
from decimal import Decimal
from datetime import datetime
from zoneinfo import ZoneInfo
from tasks import request_from_ai
from typing import AsyncGenerator
from dataclasses import dataclass
from internal.repo import Repository
from fastapi import UploadFile, Request
from configuration import RAW_REPORT_FILE_PATH
from internal.shemas import Report, ReportPath
from internal.midleware import CustomHTTPException
from utils import download_files, TaskCondition, get_status


@dataclass(slots=True, frozen=True, init=True)
class ReportService:
    repository: Repository

    async def add(self, flat_id: int, dirty_photos: list[UploadFile]) -> Report:

        async with self.repository.transaction() as repo:
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


    async def get_reports(self, user_id: int) -> list[Report]:
        async with self.repository.transaction() as repo:
            res: list[Report] = await repo.Report.get_reports(user_id)
        return res


    async def get_an_flat(self, flat_id: int) -> list[Report]:
        async with self.repository.transaction() as repo:
            res: list[Report] = await repo.Report.get_an_flat(flat_id)
        return res


    async def get_current(self, report_id: int) -> list[ReportPath]:
        async with self.repository.transaction() as repo:
            res: list[ReportPath] = await repo.Report.get_current(report_id)
        return res


    async def delete_report(self, report_id: int) -> int:
        async with self.repository.transaction() as repo:
            res: int = await repo.Report.delete_report(report_id)
        return res


    @staticmethod
    async def task(report_id: int, request: Request)-> AsyncGenerator[str, None]:

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