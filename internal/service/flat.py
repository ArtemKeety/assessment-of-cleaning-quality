import asyncio
from fastapi_babel import _
from fastapi import UploadFile
from utils import download_files
from dataclasses import dataclass
from internal.repo import Repository
from internal.shemas import Flat, FullFlat
from internal.midleware import CustomHTTPException
from configuration import FLAT_FILE_PATH, MAX_COUNT


@dataclass(init=True, slots=True, frozen=True)
class FlatService:
    repository: Repository

    async def add(self, name: str, user_id: int, photos: list[UploadFile]) -> Flat:

        async with self.repository.transaction(tr="serializable") as repo:

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


    async def all(self, user_id: int) -> list[Flat]:
        async with self.repository.transaction() as repo:
            res: list[Flat] = await repo.Flat.all(user_id)
        return  res


    async def get_id(self, flat_id: int) -> list[FullFlat]:
        async with self.repository.transaction() as repo:
            res: list[FullFlat] = await repo.Flat.get_id(flat_id)
        return res


    async def delete(self, flat_id: int) -> int:
        async with self.repository.transaction() as repo:
            res: int =  await repo.Flat.delete(flat_id)
        return  res