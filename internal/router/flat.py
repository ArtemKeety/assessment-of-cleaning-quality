from internal.service import Service
from internal.shemas import Flat, FullFlat
from fastapi import APIRouter, Depends, UploadFile, Body
from internal.midleware import user_identy, ValidateFiles, CustomRateLimit


router = APIRouter(prefix="/flat")


@router.post("/add", response_model=Flat)
async def add_flat(
        name: str = Body(),
        photos: list[UploadFile] = Depends(ValidateFiles()),
        user_data = Depends(CustomRateLimit(2, minute=1)),
        service = Depends(Service.from_request)
):
    return await service.Flat.add(name, user_data.get('user_id'), photos)

@router.get('/all', response_model=list[Flat])
async def get_flats(user_data = Depends(user_identy), service = Depends(Service.from_request)):
    return await service.Flat.all(user_data.get('user_id'))

@router.get('/{flat_id}', response_model=list[FullFlat])
async def get_id(flat_id: int, service = Depends(Service.from_request)):
    return await service.Flat.get_id(flat_id)

@router.delete('/{flat_id}',response_model=int, dependencies=[Depends(user_identy)])
async def delete(flat_id: int, service = Depends(Service.from_request)):
    return await service.Flat.delete(flat_id)
