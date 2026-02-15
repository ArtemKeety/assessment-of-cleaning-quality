from typing import Annotated
from configuration import FILE_SIZE
from database import PostgresSession
from internal.service import Service
from fastapi import Depends, UploadFile
from internal.repository import Repository
from internal.midleware import ValidateFiles, get_header_data


async def layer(session: PostgresSession) -> Service:
    repo = Repository(session)
    service = Service(repo)
    return service

LayerDep  = Annotated[Service, Depends(layer)]

UserAgent = Annotated[str, Depends(get_header_data)]

Photos = Annotated[list[UploadFile], Depends(ValidateFiles(10, FILE_SIZE, ".jpg", ".png"))]

