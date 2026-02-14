from utils import TransactionEnum
from internal.shemas import Flat, FullFlat
from fastapi import APIRouter, Depends, UploadFile, Body
from internal.midleware import user_identy, ValidateFiles, CustomRateLimit
from internal.layer import Layer
from internal.service import Service


router = APIRouter(prefix="/flat")


@router.post("/add", response_model=Flat)
async def add_flat(
        name: str = Body(),
        photos: list[UploadFile] = Depends(ValidateFiles()),
        user_data = Depends(CustomRateLimit(2, minute=1)),
        service:Service = Depends(Layer(TransactionEnum.serializable))
):
    return await service.Flat.add(name, user_data.get('user_id'), photos)

@router.get('/all', response_model=list[Flat])
async def get_flats(user_data = Depends(user_identy), service:Service = Depends(Layer())):
    return await service.Flat.all(user_data.get('user_id'))

@router.get('/{flat_id}', response_model=list[FullFlat])
async def get_id(flat_id: int, service = Depends(Layer())):
    return await service.Flat.get_id(flat_id)

@router.delete('/{flat_id}',response_model=None, dependencies=[Depends(user_identy)], status_code=204)
async def delete(flat_id: int, service:Service = Depends(Layer())):
    return await service.Flat.delete(flat_id)
