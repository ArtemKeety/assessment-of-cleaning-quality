from internal.shemas import Pagination
from .dependecies import LayerDep, Photos
from internal.shemas import Report, ReportPath
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Body, Request, Query, Depends
from internal.midleware import user_identy, UserIdenty, CustomRateLimit


router = APIRouter(prefix="/report")


@router.post("/add", response_model=Report, dependencies=[Depends(CustomRateLimit(1, minute=3))])
async def add(
        photos: Photos,
        service: LayerDep,
        flat_id: int = Body(),
):
    return await service.Report.add(flat_id, photos)


@router.get("/all", response_model=list[Report], description="Запросить все отчёты у пользователя")
async def reports(user_data: UserIdenty, service: LayerDep, pages: Pagination=Query()):
    return await service.Report.get_reports(user_data.get("user_id"), pages)


@router.get("/flat/{flat_id}",
    response_model=list[Report],
    description="Запросить все отчёты по квартире",
    dependencies=[Depends(user_identy)],
)
async def get_an_flat(flat_id: int, service: LayerDep, pages: Pagination=Query()):
    return await service.Report.get_an_flat(flat_id, pages)


@router.get('/{report_id}', response_model=list[ReportPath], description="Показать полность отчёт по id")
async def current_report(report_id: int, service: LayerDep):
    return await service.Report.get_current(report_id)


@router.get('/task/{report_id}', response_class=StreamingResponse)
async def task(report_id: int, request: Request, service: LayerDep):
    return StreamingResponse(service.Report.task(report_id, request), media_type="text/event-stream")


@router.delete('/{report_id}', response_model=None, dependencies=[Depends(user_identy)], status_code=204)
async def del_report(report_id: int, service: LayerDep):
    return await service.Report.delete_report(report_id)
