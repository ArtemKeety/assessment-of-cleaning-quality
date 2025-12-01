import uuid
from repo import UserRepo
from utils import Password
from database import RedisDb
from asyncpg import Connection
from midleware import CustomHTTPException
from shemas import UserRegister, UserLogin



class UserService:

    @staticmethod
    async def sign_up(u: UserRegister, agent: str, redis: RedisDb, conn: Connection) -> str:
        if user := await UserRepo.get_user(u, conn):
            raise CustomHTTPException(status_code=409, detail="User already exists")

        u.password = Password.hash_password(u.password)

        if not (user_id := await UserRepo.add_user(u, conn)):
            raise CustomHTTPException(status_code=501, detail="Error adding user")

        session: str = f"{u.password}.{user_id}.{uuid.uuid4()}"

        await redis.add(session, {"User-Agent": agent, "user_id": user_id})

        return session


    @staticmethod
    async def sign_in(u: UserLogin, agent:str, redis: RedisDb, conn: Connection)->str:
        if not (user := await UserRepo.get_user(u, conn)):
            raise CustomHTTPException(status_code=400, detail="Error getting user")

        if not Password.verify(user.password, u.password):
            raise CustomHTTPException(status_code=400, detail="Error verifying password")

        session: str = f"{user.password}.{user.id}.{uuid.uuid4()}"

        await redis.add(session, {"User-Agent": agent, "user_id": user.id})

        return session


    @staticmethod
    async def del_user(user_id : int, conn: Connection) -> int:
        return await UserRepo.del_user(user_id, conn)