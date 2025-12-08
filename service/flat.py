import asyncio
import asyncpg
from repo import FlatRepo
from fastapi import UploadFile
from utils import download_files
from shemas import Flat, FullFlat
from configuration import FLAT_FILE_PATH
from midleware import CustomHTTPException

class FlatService:

    @staticmethod
    async def add(name: str, user_id: int, photos: list[UploadFile], conn: asyncpg.Connection) -> Flat:

        download_task = asyncio.create_task(download_files(photos, FLAT_FILE_PATH))

        flat_id = await FlatRepo.add_flat(name, user_id, photos[0], conn)

        if not await FlatRepo.add_flat_photo(photos, flat_id, conn):
            await FlatRepo.delete(flat_id, conn)
            download_task.cancel()
            raise CustomHTTPException(status_code=501, detail="Error adding flat and photos")

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