import asyncpg
from fastapi import UploadFile
from customlogger import LOGGER
from shemas import Flat, FullFlat
from midleware import CustomHTTPException



class FlatRepo:

    @staticmethod
    async def add_flat(name: str, user_id: int, preview: UploadFile, conn: asyncpg.Connection) -> int:
        if res := await conn.fetchval(
            "INSERT INTO flat (name, user_id, preview) VALUES ($1, $2, $3) RETURNING id",
                name, user_id, preview.filename
        ):
            return res
        raise CustomHTTPException(status_code=501, detail="error in adding flat")

    @staticmethod
    async def add_flat_photo(photos: list[UploadFile], flat_id: int, conn: asyncpg.Connection) -> bool:
        try:
            req = await conn.prepare('INSERT INTO photo (path, flat_id) VALUES ($1, $2)')
            async with conn.transaction():
                for photo in photos:
                    await req.fetchval(photo.filename, flat_id)
            return True
        except BaseException as e:
            LOGGER.error(f"{type(e).__name__}: {e}")
            return False


    @staticmethod
    async def delete(flat_id: int, conn: asyncpg.Connection) -> bool:
        if res := await conn.fetchval(
            "DELETE FROM flat WHERE id = $1 RETURNING id",
                flat_id
        ):
            return res
        raise CustomHTTPException(status_code=404, detail="error in deleting flat")


    @staticmethod
    async def all(user_id: int, conn: asyncpg.Connection) -> list[Flat]:
        if res := await conn.fetch(
            "SELECT id, name, preview FROM flat WHERE user_id = $1",
            user_id
        ):
            return [Flat(**obj) for obj in res]
        return []

    @staticmethod
    async def get_id(flat_id: int, conn: asyncpg.Connection) -> list[FullFlat]:
        if res := await conn.fetch(
            """
                select p.id, p.path
                from flat f
                join photo p on f.id = p.flat_id
                where f.id = $1
            """,
            flat_id,
        ):
            return [FullFlat(**obj) for obj in res]
        raise CustomHTTPException(status_code=404, detail="Not found flat full data")



