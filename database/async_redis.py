import orjson
from typing import Optional, Any, AsyncGenerator
from fastapi import Request
import redis.asyncio as redis
from customlogger import LOGGER
from redis.asyncio.client import Pipeline
from contextlib import asynccontextmanager
from configuration import LIFE_TIME, RedisConfig


class RedisDb:

    __slots__ = '__client'

    def __init__(self):
        self.__client = redis.Redis(
            host=RedisConfig.host,
            port=RedisConfig.port,
            db=RedisConfig.db,
            decode_responses=RedisConfig.decode_responses,
            max_connections=RedisConfig.max_connections,
        )

    async def add(self, key: str, value: dict, exp: int = LIFE_TIME):
        await self.__client.set(key, orjson.dumps(value), ex=exp)

    async def new_expire(self, key: str, exp: int = LIFE_TIME):
        await self.__client.expire(key, time=exp)

    async def delete(self, key: str):
        await self.__client.delete(key)

    async def get(self, key: str) -> Optional[dict]:
        if res := await self.__client.get(key):
            return orjson.loads(res)
        return None

    async def ping(self):
        res = await self.__client.ping()
        LOGGER.info(f"Redis connect: {res}")

    async def disconnect(self) -> None:
        await self.__client.close()
        LOGGER.info("Redis disconnected")

    @staticmethod
    async def from_request_conn(request: Request) -> 'RedisDb':
        return request.app.state.redis_pool

    @asynccontextmanager
    async def pipe_line(self, transaction: bool=False)-> AsyncGenerator[Pipeline, Any]:
        async with self.__client.pipeline(transaction=transaction) as pipe:
            yield pipe

