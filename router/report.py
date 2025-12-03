import asyncpg
from database import DataBase
from service import ReportService
from shemas import Report, ReportPath
from midleware import user_identy, valid_files
from fastapi import APIRouter, UploadFile, Depends, BackgroundTasks
from fastapi_limiter.depends import RateLimiter

router = APIRouter(prefix="/report")


@router.post(
    "/add",
    response_model=int,
    dependencies=[Depends(user_identy), Depends(RateLimiter(times=6, minutes=1))]
)
async def add(
        flat_id: int,
        photos: list[UploadFile]=Depends(valid_files),
        conn: asyncpg.Connection = Depends(DataBase.from_request_conn),
):
    return await ReportService.add(flat_id, photos, conn)


@router.get(
    "/all",
    response_model=list[Report],
    description="Запросить все отчёты у пользователя",
    dependencies=[Depends(RateLimiter(times=6, minutes=1))]
)
async def reports(user_data = Depends(user_identy), conn: asyncpg.Connection = Depends(DataBase.from_request_conn)):
    return await ReportService.get_reports(user_data.get("user_id"), conn)


@router.get(
    "/flat/{flat_id}",
    response_model=list[Report],
    description="Запросить все отчёты по квартире",
    dependencies=[Depends(user_identy), Depends(RateLimiter(times=6, minutes=1))]
)
async def get_an_flat(flat_id: int, conn: asyncpg.Connection = Depends(DataBase.from_request_conn)):
    return await ReportService.get_an_flat(flat_id, conn)


@router.get(
    '/{report_id}',
    response_model=list[ReportPath],
    description="Показать полность отчёт по id",
    dependencies=[Depends(RateLimiter(times=6, minutes=1))]
)
async def current_report(report_id: int, conn: asyncpg.Connection = Depends(DataBase.from_request_conn)):
    return await ReportService.get_current(report_id, conn)


@router.delete(
    '/{report_id}',
    response_model=int,
    dependencies=[Depends(user_identy), Depends(RateLimiter(times=6, minutes=1))]
)
async def del_report(report_id: int, conn: asyncpg.Connection = Depends(DataBase.from_request_conn)):
    return await ReportService.delete_report(report_id, conn)
