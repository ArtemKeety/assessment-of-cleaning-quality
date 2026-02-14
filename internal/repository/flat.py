import asyncpg
from fastapi_babel import _
from fastapi import UploadFile
from dataclasses import dataclass
from internal.shemas import Flat, FullFlat
from internal.midleware import CustomHTTPException


@dataclass(slots=True, frozen=True, init=True)
class FlatRepo:
    conn: asyncpg.Connection


    async def add_flat(self, name: str, user_id: int, preview: UploadFile) -> int:
        if res := await self.conn.fetchval(
            "INSERT INTO flat (name, user_id, preview) VALUES ($1, $2, $3) RETURNING id",
                name, user_id, preview.filename
        ):
            return res
        raise CustomHTTPException(status_code=501, detail=_("Error in adding flat"))


    async def add_flat_photo(self, photos: list[UploadFile], flat_id: int) -> None:
        req = await self.conn.prepare('INSERT INTO photo (path, flat_id) VALUES ($1, $2)')
        for photo in photos:
            await req.fetchval(photo.filename, flat_id)


    async def delete(self, flat_id: int) -> int:
        if res := await self.conn.fetchval(
            "DELETE FROM flat WHERE id = $1 RETURNING id",
                flat_id
        ):
            return res
        raise CustomHTTPException(status_code=404, detail=_("Error in deleting flat"))


    async def all(self, user_id: int) -> list[Flat]:
        if res := await self.conn.fetch(
            "SELECT id, name, preview FROM flat WHERE user_id = $1",
            user_id
        ):
            return [Flat(**obj) for obj in res]
        return []

    async def get_id(self, flat_id: int) -> list[FullFlat]:
        if res := await self.conn.fetch(
            """
                select p.id, p.path
                from flat f
                join photo p on f.id = p.flat_id
                where f.id = $1
            """,
            flat_id,
        ):
            return [FullFlat(**obj) for obj in res]
        raise CustomHTTPException(status_code=404, detail=_("Not found flat full data"))


    async def count(self, user_id: int) -> int:
        return await self.conn.fetchval("select count(*) from flat where user_id = $1", user_id)


    async def lock(self, key: int) -> None:
        await self.conn.execute('select pg_advisory_xact_lock($1)', key)