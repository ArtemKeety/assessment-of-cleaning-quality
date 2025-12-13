import asyncpg
from database import DataBase
from internal.service import FlatService
from internal.shemas import Flat, FullFlat
from fastapi import APIRouter, Depends, UploadFile, Body
from internal.midleware import user_identy, ValidateFiles, CustomRateLimit

router = APIRouter(prefix="/flat")


@router.post("/add", response_model=Flat)
async def add_flat(
        name: str = Body(),
        photos: list[UploadFile] = Depends(ValidateFiles()),
        user_data = Depends(CustomRateLimit(1, minute=3)),
        conn: asyncpg.Connection = Depends(DataBase.from_request_conn)
):
    return await FlatService.add(name, user_data.get('user_id'), photos, conn)

@router.get('/all', response_model=list[Flat])
async def get_flats(
        user_data = Depends(user_identy),
        conn: asyncpg.Connection = Depends(DataBase.from_request_conn)):
    return await FlatService.all(user_data.get('user_id'), conn)

@router.get('/{flat_id}', response_model=list[FullFlat])
async def get_id(flat_id: int, conn: asyncpg.Connection = Depends(DataBase.from_request_conn)):
    return await FlatService.get_id(flat_id, conn)

@router.delete('/{flat_id}',response_model=int, dependencies=[Depends(user_identy)])
async def delete(flat_id: int, conn: asyncpg.Connection = Depends(DataBase.from_request_conn)):
    return await FlatService.delete(flat_id, conn)
