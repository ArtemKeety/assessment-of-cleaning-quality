import asyncpg
from .flat import FlatRepo
from .user import UserRepo
from .report import ReportRepo
from database import DataBase
from datetime import datetime
from fastapi import UploadFile
from customlogger import LOGGER
from contextlib import asynccontextmanager
from utils.isolation_lvl import TransactionEnum
from typing import Protocol, Optional, Any, AsyncGenerator
from internal.shemas import Flat, FullFlat, Report, ReportPath, UserLogin, User


class IFlatRepo(Protocol):
    async def add_flat(self, name: str, user_id: int, preview: UploadFile) -> int:
        ...

    async def add_flat_photo(self, photos: list[UploadFile], flat_id: int) -> None:
        ...

    async def delete(self, flat_id: int) -> int:
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

    async def del_report(self, report_id: int) -> int:
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

    async def del_user(self, user_id: int) -> int:
        ...



class UoWRepository:

    __slots__ = 'pool','User', 'Flat', 'Report',

    def __init__(self, pool: DataBase):
        self.pool: DataBase = pool
        self.User: Optional[IRepoUser] = None
        self.Flat: Optional[IFlatRepo] = None
        self.Report: Optional[IRepoReport] = None

    def init_repo(self, conn: asyncpg.Connection):
        self.User: Optional[IRepoUser] = UserRepo(conn)
        self.Flat: Optional[IFlatRepo] = FlatRepo(conn)
        self.Report: Optional[IRepoReport] = ReportRepo(conn)

    def clear_repo(self):
        self.User: Optional[IRepoUser] = None
        self.Flat: Optional[IFlatRepo] = None
        self.Report: Optional[IRepoReport] = None


    @asynccontextmanager
    async def transaction(self, tr: str = "read_committed") -> AsyncGenerator['UoWRepository', Any]:
        async with self.pool.acquire() as conn:
            async with conn.transaction(isolation=TransactionEnum(tr)):
                try:
                    self.init_repo(conn)
                    yield self
                except Exception as e:
                    LOGGER.warning(f"{type(e).__name__}: {e}")
                    raise
                finally:
                    self.clear_repo()



