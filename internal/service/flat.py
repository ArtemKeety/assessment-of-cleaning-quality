import asyncio
from fastapi_babel import _
from fastapi import UploadFile
from utils import download_files
from dataclasses import dataclass
from utils.isolation_lvl import IsolationLvl
from internal.midleware import CustomHTTPException
from configuration import FLAT_FILE_PATH, MAX_COUNT
from internal.shemas import Flat, FullFlat, Pagination
from internal.repository import Transaction, IRepository


@dataclass(init=True, slots=True, frozen=True)
class FlatService:
    repository: IRepository

    async def add(self, name: str, user_id: int, photos: list[UploadFile]) -> Flat:

        async with Transaction(self.repository, IsolationLvl.serializable) as repo:

            if MAX_COUNT <= await repo.Flat.count(user_id):
                raise CustomHTTPException(
                    detail=_("A user cannot have a flat of more than") + f" {MAX_COUNT}",
                    status_code=400,
                )

            download_task: asyncio.Task = asyncio.create_task(download_files(photos, FLAT_FILE_PATH))

            flat_id = await repo.Flat.add_flat(name, user_id, photos[0])

            await repo.Flat.add_flat_photo(photos, flat_id)

            await download_task

        return Flat(id=flat_id, name=name, preview=photos[0].filename)


    async def all(self, user_id: int, pages: Pagination) -> list[Flat]:
        return await self.repository.Flat.all(user_id, pages)


    async def get_id(self, flat_id: int) -> list[FullFlat]:
        return await self.repository.Flat.get_id(flat_id)


    async def delete(self, flat_id: int) -> None:
        return await self.repository.Flat.delete(flat_id)
