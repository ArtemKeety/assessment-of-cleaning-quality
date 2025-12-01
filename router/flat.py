import asyncpg
from database import DataBase
from service import FlatService
from shemas import Flat, FullFlat
from midleware import user_identy, valid_files
from fastapi_limiter.depends import RateLimiter
from fastapi import APIRouter, Depends, UploadFile


router = APIRouter(prefix="/flat")


@router.post(
    "/add",
    response_model=int,
    dependencies=[Depends(RateLimiter(times=6, minutes=1))]
)
async def add_flat(
        name: str,
        photos: list[UploadFile] = Depends(valid_files),
        user_data = Depends(user_identy),
        conn: asyncpg.Connection = Depends(DataBase.from_request_conn)
):
    return await FlatService.add(name, user_data.get('user_id'), photos, conn)

@router.get(
    '/all',
    response_model=list[Flat],
    dependencies=[Depends(RateLimiter(times=6, minutes=1))]
)
async def get_flats(user_data = Depends(user_identy), conn: asyncpg.Connection = Depends(DataBase.from_request_conn)):
    return await FlatService.all(user_data.get('user_id'), conn)

@router.get(
    '/{flat_id}',
    response_model=list[FullFlat],
    dependencies=[Depends(RateLimiter(times=6, minutes=1))]
)
async def get_id(flat_id: int, conn: asyncpg.Connection = Depends(DataBase.from_request_conn)):
    return await FlatService.get_id(flat_id, conn)

@router.delete(
    '/{flat_id}',
    response_model=int,
    dependencies=[Depends(user_identy), Depends(RateLimiter(times=6, minutes=1))]
)
async def delete(flat_id: int, conn: asyncpg.Connection = Depends(DataBase.from_request_conn)):
    return await FlatService.delete(flat_id, conn)
