from typing import Annotated
from configuration import FILE_SIZE
from database import PostgresSession
from fastapi import Depends, UploadFile
from internal.service import Service, IService
from internal.repository import Repository, IRepository
from internal.midleware import ValidateFiles, get_header_data


async def layer(session: PostgresSession) -> IService:
    repo: IRepository = Repository(session)
    service: IService = Service(repo)
    return service

LayerDep = Annotated[IService, Depends(layer)]

UserAgent = Annotated[str, Depends(get_header_data)]

Photos = Annotated[list[UploadFile], Depends(ValidateFiles(10, FILE_SIZE, ".jpg", ".png"))]

