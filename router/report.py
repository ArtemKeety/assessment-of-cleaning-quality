import asyncpg
from database import DataBase
from service import ReportService
from shemas import Report, ReportPath
from fastapi import APIRouter, UploadFile, Depends, Body
from midleware import user_identy, valid_files, CustomRateLimit


router = APIRouter(prefix="/report")


@router.post("/add", response_model=Report, dependencies=[Depends(CustomRateLimit(1, minute=3))])
async def add(
        flat_id: int = Body(),
        photos: list[UploadFile]=Depends(valid_files),
        conn: asyncpg.Connection = Depends(DataBase.from_request_conn),
):
    return await ReportService.add(flat_id, photos, conn)


@router.get("/all", response_model=list[Report], description="Запросить все отчёты у пользователя")
async def reports(user_data = Depends(user_identy), conn: asyncpg.Connection = Depends(DataBase.from_request_conn)):
    return await ReportService.get_reports(user_data.get("user_id"), conn)


@router.get("/flat/{flat_id}",
    response_model=list[Report],
    description="Запросить все отчёты по квартире",
    dependencies=[Depends(user_identy)]
)
async def get_an_flat(flat_id: int, conn: asyncpg.Connection = Depends(DataBase.from_request_conn)):
    return await ReportService.get_an_flat(flat_id, conn)


@router.get('/{report_id}', response_model=list[ReportPath], description="Показать полность отчёт по id")
async def current_report(report_id: int, conn: asyncpg.Connection = Depends(DataBase.from_request_conn)):
    return await ReportService.get_current(report_id, conn)


@router.delete('/{report_id}', response_model=int, dependencies=[Depends(user_identy)])
async def del_report(report_id: int, conn: asyncpg.Connection = Depends(DataBase.from_request_conn)):
    return await ReportService.delete_report(report_id, conn)
