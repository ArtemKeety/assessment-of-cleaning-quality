from database import RedisSession
from fastapi import UploadFile, Request
from internal.repository import IRepository
from typing import Protocol, AsyncGenerator, Any
from internal.shemas import Flat, FullFlat, Report, ReportPath, UserRegister, Session, UserLogin


class IFlatService(Protocol):

    async def add(self, name: str, user_id: int, photos: list[UploadFile]) -> Flat:
        ...

    async def all(self, user_id: int) -> list[Flat]:
        ...

    async def get_id(self, flat_id: int) -> list[FullFlat]:
        ...

    async def delete(self, flat_id: int) -> None:
        ...


class IReportService(Protocol):

    async def add(self, flat_id: int, dirty_photos: list[UploadFile]) -> Report:
        ...

    async def get_reports(self, user_id: int) -> list[Report]:
        ...

    async def get_an_flat(self, flat_id: int) -> list[Report]:
        ...

    async def get_current(self, report_id: int) -> list[ReportPath]:
        ...

    async def delete_report(self, report_id: int) -> None:
        ...

    @staticmethod
    def task(report_id: int, request: Request)-> AsyncGenerator[Any, Any]:
        ...


class IUserService(Protocol):

    async def sign_up(self, u: UserRegister, agent: str, redis: RedisSession) -> Session:
        ...

    async def sign_in(self, u: UserLogin, agent: str, redis: RedisSession) -> Session:
        ...

    async def del_user(self, user_id: int) -> None:
        ...

class IService(Protocol):
    User: IUserService
    Flat: IFlatService
    Report: IReportService

    __slots__ = ('User', 'Flat', 'Report')

    def __init__(self, repo: IRepository):
        ...



