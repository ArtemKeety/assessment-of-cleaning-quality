
from datetime import datetime
from fastapi import UploadFile
from typing import Protocol, Optional
from internal.shemas import Flat, FullFlat, Report, ReportPath, UserLogin, User, Pagination


class IFlatRepo(Protocol):
    async def add_flat(self, name: str, user_id: int, preview: UploadFile) -> int:
        ...

    async def add_flat_photo(self, photos: list[UploadFile], flat_id: int) -> None:
        ...

    async def delete(self, flat_id: int) -> None:
        ...

    async def all(self, user_id: int, pages: Pagination) -> list[Flat]:
        ...

    async def get_id(self, flat_id: int) -> list[FullFlat]:
        ...

    async def count(self, user_id: int) -> int:
        ...

    async def lock(self, key: int) -> None:
        ...

class IReportRepo(Protocol):
    async def add_report_place(self, flat_id: int, path: str, date: datetime) -> int:
        ...

    async def add_report_photo_raw(self, report_id: int, info: str, photo: str, count: int) -> None:
        ...

    async def del_report(self, report_id: int) -> None:
        ...

    async def get_reports(self, user_id: int, pages: Pagination) -> list[Report]:
        ...

    async def get_an_flat(self, flat_id: int, pages: Pagination) -> list[Report]:
        ...

    async def get_current(self, report_id: int) -> list[ReportPath]:
        ...

class IUserRepo(Protocol):
    async def get_user(self, u: UserLogin) -> Optional[User]:
        ...

    async def add_user(self, u: UserLogin) -> int:
        ...

    async def del_user(self, user_id: int) -> None:
        ...



