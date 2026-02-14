import uuid
from utils import Password
from fastapi_babel import _
from database import RedisDb
from dataclasses import dataclass
from internal.repo import Repository
from internal.midleware import CustomHTTPException
from internal.shemas import UserRegister, UserLogin, Session

@dataclass(slots=True, frozen=True, init=True)
class UserService:
    repository: Repository

    async def sign_up(self, u: UserRegister, agent: str, redis: RedisDb) -> Session:
        async with self.repository.transaction() as repo:

            if await repo.User.get_user(u):
                raise CustomHTTPException(status_code=409, detail=_("User already exists"))

            u.password = Password.hash_password(u.password)

            if not (user_id := await repo.User.add_user(u)):
                raise CustomHTTPException(status_code=501, detail=_("Error adding user"))

        session: str = f"{u.password}.{user_id}.{uuid.uuid4()}"

        await redis.add(session, {"User-Agent": agent, "user_id": user_id})

        return Session(session=session)


    async def sign_in(self, u: UserLogin, agent:str, redis: RedisDb) -> Session:
        async with self.repository.transaction() as repo:
            if not (user := await repo.User.get_user(u)):
                raise CustomHTTPException(status_code=400, detail=_("Error getting user"))

        if not Password.verify(user.password, u.password):
            raise CustomHTTPException(status_code=400, detail=_("Error verifying password"))

        session: str = f"{user.password}.{user.id}.{uuid.uuid4()}"

        await redis.add(session, {"User-Agent": agent, "user_id": user.id})

        return Session(session=session)


    async def del_user(self, user_id : int) -> int:
        async with self.repository.transaction() as repo:
            res: int = await repo.User.get_user(user_id)
        return res