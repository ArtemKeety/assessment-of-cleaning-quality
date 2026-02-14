import asyncpg
from typing import Optional
from fastapi_babel import _
from dataclasses import dataclass
from internal.shemas import UserLogin, User
from internal.midleware import CustomHTTPException


@dataclass(slots=True, frozen=True, init=True)
class UserRepo:
    conn: asyncpg.Connection


    async def get_user(self, u: UserLogin)-> Optional[User]:
        if res := await self.conn.fetchrow(
            "SELECT * FROM users u WHERE u.login = $1 and u.is_active = true",
            u.login
        ):
            return User(**res)
        return None


    async def add_user(self, u: UserLogin) -> int:
        return await self.conn.fetchval(
            "insert into users (login, password) values($1, $2) returning id",
            u.login, u.password
        )


    async def del_user(self, user_id : int) -> int:
        if res := await self.conn.fetchval(
            "Update users Set is_active = $1 where id = $2 returning id",
            False, user_id
        ):
            return res
        raise CustomHTTPException(detail=_("Error in deleting user"), status_code=501)
