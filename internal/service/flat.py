import asyncio
import asyncpg
from fastapi_babel import _
from fastapi import UploadFile
from utils import download_files
from internal.repo import FlatRepo
from internal.shemas import Flat, FullFlat
from internal.midleware import CustomHTTPException
from configuration import FLAT_FILE_PATH, MAX_COUNT


class FlatService:

    @staticmethod
    async def add(name: str, user_id: int, photos: list[UploadFile], conn: asyncpg.Connection) -> Flat:

        async with conn.transaction(isolation='serializable'):

            if MAX_COUNT <= await FlatRepo.count(user_id, conn):
                raise CustomHTTPException(
                    detail=_("A user cannot have a flat of more than") + f" {MAX_COUNT}",
                    status_code=400,
                )

            download_task: asyncio.Task = asyncio.create_task(download_files(photos, FLAT_FILE_PATH))

            flat_id = await FlatRepo.add_flat(name, user_id, photos[0], conn)

            await FlatRepo.add_flat_photo(photos, flat_id, conn)

            await download_task

        return Flat(id=flat_id, name=name, preview=photos[0].filename)

    @staticmethod
    async def all(user_id: int, conn: asyncpg.Connection) -> list[Flat]:
        return await FlatRepo.all(user_id, conn)

    @staticmethod
    async def get_id(flat_id: int, conn: asyncpg.Connection) -> list[FullFlat]:
        return await FlatRepo.get_id(flat_id, conn)

    @staticmethod
    async def delete(flat_id: int, conn: asyncpg.Connection) -> int:
        return await FlatRepo.delete(flat_id, conn)