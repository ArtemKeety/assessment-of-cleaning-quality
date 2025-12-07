from typing import Any
from .auth import user_identy
from fastapi import Depends, Request, Response
from fastapi_limiter.depends import RateLimiter


class CustomRateLimit:
    __slots__ = ('__times', '__count')

    def __init__(self, count: int, sec:int=1, minute:int=0, hour: int=0, day:int=0):
        self.__times: int = sec + minute * 60 + hour * 3600 + day * 86400
        self.__count = count

    @staticmethod
    async def __get_user_id(r: Request):
        return f"user_id:{r.state.user_id}"

    async def __call__(self, r: Request, res: Response, user_data = Depends(user_identy)) -> Any:
        limit = RateLimiter(times=self.__count, seconds=self.__times, identifier=self.__get_user_id)
        await limit(request=r, response=res)
        return user_data


