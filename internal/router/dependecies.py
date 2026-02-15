from typing import Annotated, Any
from configuration import FILE_SIZE
from database import PostgresSession
from internal.service import Service
from fastapi import Depends, UploadFile
from internal.repository import Repository
from internal.midleware import ValidateFiles, CustomRateLimit, get_header_data


async def layer(session: PostgresSession) -> Service:
    repo = Repository(session)
    service = Service(repo)
    return service

LayerDep  = Annotated[Service, Depends(layer)]

UserAgent = Annotated[str, Depends(get_header_data)]

Photos = Annotated[list[UploadFile], Depends(ValidateFiles(10, FILE_SIZE, ".jpg", ".png"))]

time_limit_small = Depends(CustomRateLimit(2, minute=1))
TimeLimitSmall = Annotated[dict[str, Any], time_limit_small]

time_limit_long = Depends(CustomRateLimit(1, minute=3))
TimeLimitLong = Annotated[dict[str, Any], time_limit_long]
