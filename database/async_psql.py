


import asyncpg

from customlogger import LOGGER
from typing import AsyncGenerator, Optional
from configuration import PsqlConfig
from contextlib import asynccontextmanager


class DataBase:
    __slots__ = ("__pool", )

    def __init__(self, config: PsqlConfig) -> None:
        self.__pool: asyncpg.Pool = asyncpg.create_pool(
            host=config.host,
            port=config.port,
            user=config.user,
            password=config.password,
            database=config.database,
            timeout=config.timeout,
            max_size=config.max_size,
            min_size=config.min_size,
        )


    @classmethod
    async def ainit(cls, config: PsqlConfig) -> 'DataBase':
        obj = cls(config)
        await obj.__pool
        LOGGER.info("Connected to database")
        return obj

    async def disconnect(self):
        await self.__pool.close()
        LOGGER.info("Disconnected to database")

    @asynccontextmanager
    async def acquire(self)-> AsyncGenerator[asyncpg.Connection, None]:
        async with self.__pool.acquire() as conn:
            yield conn

    async def connection(self) -> asyncpg.Connection:
        return await self.__pool.acquire()

    async def close(self, conn: asyncpg.Connection) -> None:
        await self.__pool.release(conn)



