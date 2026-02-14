


import asyncpg
from fastapi import Request
from customlogger import LOGGER
from configuration import PsqlConfig

from contextlib import asynccontextmanager

from typing import Any, AsyncGenerator, Optional


class DataBase:

    __slots__ = '__pool',

    def __init__(self, pool: asyncpg.Pool) -> None:
        self.__pool = pool

    @classmethod
    async def connect(cls)-> 'DataBase':
        pool = await asyncpg.create_pool(
            host=PsqlConfig.host,
            port=PsqlConfig.port,
            user=PsqlConfig.user,
            password=PsqlConfig.password,
            database=PsqlConfig.database,
            timeout=PsqlConfig.timeout,
            max_size=PsqlConfig.max_size,
            min_size=PsqlConfig.min_size,
        )
        obj = cls(pool)
        LOGGER.info("Connected to database")
        return obj

    async def disconnect(self):
        await self.__pool.close()
        LOGGER.info("Disconnected to database")

    @asynccontextmanager
    async def acquire(self)-> AsyncGenerator[asyncpg.Connection, None]:
        async with self.__pool.acquire() as conn:
            yield conn




