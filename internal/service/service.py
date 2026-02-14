from .user import UserService
from .flat import FlatService
from database import RedisDb
from .report import ReportService
from internal.repo import Repository
from fastapi import UploadFile, Request
from typing import Protocol, AsyncGenerator
from internal.shemas import Flat, FullFlat, Report, ReportPath, UserRegister, Session, UserLogin


class FlatBase(Protocol):

    async def add(self, name: str, user_id: int, photos: list[UploadFile]) -> Flat:
        ...

    async def all(self, user_id: int) -> list[Flat]:
        ...

    async def get_id(self, flat_id: int) -> list[FullFlat]:
        ...

    async def delete(self, flat_id: int) -> int:
        ...


class ReportBase(Protocol):

    async def add(self, flat_id: int, dirty_photos: list[UploadFile]) -> Report:
        ...

    async def get_reports(self, user_id: int) -> list[Report]:
        ...

    async def get_an_flat(self, flat_id: int) -> list[Report]:
        ...

    async def get_current(self, report_id: int) -> list[ReportPath]:
        ...

    async def delete_report(self, report_id: int) -> int:
        ...

    @staticmethod
    async def task(report_id: int, request: Request):
        ...


class UserBase(Protocol):

    async def sign_up(self, u: UserRegister, agent: str, redis: RedisDb) -> Session:
        ...

    async def sign_in(self, u: UserLogin, agent: str, redis: RedisDb) -> Session:
        ...

    async def del_user(self, user_id: int) -> int:
        ...


class Service:
    __slots__ = ('User', 'Flat', 'Report')

    def __init__(self, repo: Repository):
        self.User: UserBase = UserService(repo)
        self.Flat: FlatBase = FlatService(repo)
        self.Report: ReportBase = ReportService(repo)

    @staticmethod
    async def from_request(request: Request) -> 'Service':
        return request.app.state.service
