import os
import redis.asyncio as redis
from fastapi import FastAPI
from customlogger import LOGGER
from internal.repo import Repository
from internal.service import Service
from configuration import RedisConfig
from database import RedisDb, DataBase
from fastapi_limiter import FastAPILimiter
from contextlib import asynccontextmanager
from internal.midleware import user_address

class LifeSpan:

    __slots__ = ("__paths", )

    def __init__(self, *path: str):
        self.__paths = path


    def __create_folder(self):
        for path in self.__paths:
            os.makedirs(path, exist_ok=True)


    async def __startup(self, app: FastAPI):
        self.__create_folder()
        LOGGER.warning("Starting lifespan")
        db_pool = await DataBase.connect()
        repo = Repository(db_pool)
        service = Service(repo)

        app.state.service = service
        app.state.db_pool = db_pool
        app.state.redis_pool = RedisDb()
        await app.state.redis_pool.ping()
        await FastAPILimiter.init(redis.from_url(str(RedisConfig()), encoding="utf-8"), identifier=user_address)


    @staticmethod
    async def __shutdown(app: FastAPI):
        await app.state.db_pool.disconnect()
        await app.state.redis_pool.disconnect()
        await FastAPILimiter.close()
        LOGGER.warning("Ending lifespan")


    @asynccontextmanager
    async def __call__(self, app: FastAPI):
        await self.__startup(app)
        yield
        await self.__shutdown(app)


