


import asyncpg

from customlogger import LOGGER
from typing import AsyncGenerator
from configuration import PsqlConfig
from contextlib import asynccontextmanager


class DataBase:
    __slots__ = ("__pool", )

    def __init__(self, config: PsqlConfig) -> None:
        self.__pool = asyncpg.create_pool(
            host=config.host,
            port=config.port,
            user=config.user,
            password=config.password,
            database=config.database,
            timeout=config.timeout,
            max_size=config.max_size,
            min_size=config.min_size,
        )
        LOGGER.info("Connected to database")

    async def disconnect(self):
        await self.__pool.close()
        LOGGER.info("Disconnected to database")

    @asynccontextmanager
    async def acquire(self)-> AsyncGenerator[asyncpg.Connection, None]:
        async with self.__pool.acquire() as conn:
            yield conn




