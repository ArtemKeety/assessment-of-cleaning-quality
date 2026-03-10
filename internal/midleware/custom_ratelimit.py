from datetime import time
from fastapi_babel import _
from .auth import UserIdenty
from fastapi import Request, Response
from .error import CustomHTTPException
from internal.domain import UserDomain
from dataclasses import dataclass, field
from fastapi_limiter.depends import RateLimiter


@dataclass(slots=True, init=True, frozen=True)
class CustomRateLimit:
    count: int
    times: time

    @staticmethod
    async def __get_user_id(r: Request):
        return f"user_id:{r.state.user_id}"

    async def __call__(self, r: Request, res: Response, user: UserIdenty) -> UserDomain:
        limit = RateLimiter(
            times=self.count,
            seconds=self.times.second,
            minutes=self.times.minute,
            hours=self.times.hour,
            identifier=self.__get_user_id,
            callback=self.__callback,
        )
        await limit(request=r, response=res)
        return user

    @staticmethod
    async def __callback(request: Request, response: Response, pexpire: int):
        raise CustomHTTPException(status_code=429, detail=_("Too much request"))



class RoleLimit:

    async def __call__(self, r: Request, res: Response, user: UserIdenty) -> UserDomain:
        limit = user.time_limit
        limit = CustomRateLimit(count=limit.count, times=limit.times)
        return await limit(r, res, user)