import asyncpg

from datetime import datetime
from fastapi import UploadFile
from typing import Protocol, Optional
from internal.repository.flat import FlatRepo
from internal.repository.user import UserRepo
from internal.repository.report import ReportRepo
from internal.shemas import Flat, FullFlat, Report, ReportPath, UserLogin, User


class IFlatRepo(Protocol):
    async def add_flat(self, name: str, user_id: int, preview: UploadFile) -> int:
        ...

    async def add_flat_photo(self, photos: list[UploadFile], flat_id: int) -> None:
        ...

    async def delete(self, flat_id: int) -> None:
        ...

    async def all(self, user_id: int) -> list[Flat]:
        ...

    async def get_id(self, flat_id: int) -> list[FullFlat]:
        ...

    async def count(self, user_id: int) -> int:
        ...

    async def lock(self, key: int) -> None:
        ...

class IRepoReport(Protocol):
    async def add_report_place(self, flat_id: int, path: str, date: datetime) -> int:
        ...

    async def add_report_photo_raw(self, report_id: int, info: str, photo: str, count: int) -> None:
        ...

    async def del_report(self, report_id: int) -> None:
        ...

    async def get_reports(self, user_id: int) -> list[Report]:
        ...

    async def get_an_flat(self, flat_id: int) -> list[Report]:
        ...

    async def get_current(self, report_id: int) -> list[ReportPath]:
        ...

class IRepoUser(Protocol):
    async def get_user(self, u: UserLogin) -> Optional[User]:
        ...

    async def add_user(self, u: UserLogin) -> int:
        ...

    async def del_user(self, user_id: int) -> None:
        ...



class Repository:

    __slots__ = 'pool', 'conn','User', 'Flat', 'Report',

    def __init__(self, conn: asyncpg.Connection):
        self.User: IRepoUser = UserRepo(conn)
        self.Flat: IFlatRepo = FlatRepo(conn)
        self.Report: IRepoReport = ReportRepo(conn)
