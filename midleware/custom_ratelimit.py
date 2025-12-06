
from database import RedisDb
from .auth import user_identy
from fastapi import Depends, Request
from .error import CustomHTTPException
from typing import Callable, Any


class CustomRateLimit:
    __slots__ = ('__times', '__count')

    def __init__(self, count: int, sec:int=1, minute:int=0, hour: int=0, day:int=0):
        self.__times: int = sec + minute * 60 + hour * 3600 + day * 86400
        self.__count = count

    async def __call__(self, r: Request, user_data = Depends(user_identy)) -> Any:
        redis: RedisDb = r.app.state.redis_pool
        user_key = f"user_id:{r.state.user_id}"
        async with redis.pipeLine(transaction=True) as pipe:
            pipe.set(user_key, 0, nx=True, ex=self.__times)
            pipe.incr(user_key)
            result = await pipe.execute()

        user_count =  result[1]
        if user_count > self.__count:
            raise CustomHTTPException(status_code=429, detail="Too many requests")

        return user_data


