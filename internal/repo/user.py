from typing import Optional
from fastapi_babel import _
from asyncpg import Connection
from internal.shemas import UserLogin, User
from internal.midleware import CustomHTTPException


class UserRepo:


    @staticmethod
    async def get_user(u: UserLogin, conn: Connection)-> Optional[User]:
        if res := await conn.fetchrow(
            "SELECT * FROM users u WHERE u.login = $1 and u.is_active = true",
            u.login
        ):
            return User(**res)
        return None


    @staticmethod
    async def add_user(u: UserLogin, conn: Connection) -> int:
        return await conn.fetchval(
            "insert into users (login, password) values($1, $2) returning id",
            u.login, u.password
        )

    @staticmethod
    async def del_user(user_id : int, conn: Connection) -> int:
        if res := await conn.fetchval(
            "Update users Set is_active = $1 where id = $2 returning id",
            False, user_id
        ):
            return res
        raise CustomHTTPException(detail=_("Error in deleting user"), status_code=501)
