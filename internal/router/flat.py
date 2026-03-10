from datetime import time
from internal.domain import UserDomain
from .dependecies import LayerDep, Photos
from fastapi import APIRouter, Body, Query, Depends
from internal.shemas import Flat, FullFlat, Pagination
from internal.midleware import user_identy, UserIdenty, CustomRateLimit


router = APIRouter(prefix="/api/v1")


@router.post("/add", response_model=Flat)
async def add_flat(
        photos: Photos,
        service: LayerDep,
        name: str = Body(),
        user: UserDomain = Depends(CustomRateLimit(2, time(minute=1))),
):
    return await service.Flat.add(name, user, photos)

@router.get('/all', response_model=list[Flat])
async def get_flats(user: UserIdenty, service: LayerDep, pages: Pagination=Query()):
    return await service.Flat.all(user,  pages)

@router.get('/{flat_id}', response_model=list[FullFlat])
async def get_id(flat_id: int, service: LayerDep):
    return await service.Flat.get_id(flat_id)

@router.delete('/{flat_id}', response_model=None, dependencies=[Depends(user_identy)], status_code=204)
async def delete(flat_id: int, service: LayerDep):
    return await service.Flat.delete(flat_id)
