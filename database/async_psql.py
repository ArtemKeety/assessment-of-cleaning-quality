import asyncpg

from customlogger import LOGGER
from configuration import PsqlConfig
from typing import AsyncGenerator, Annotated
from contextlib import asynccontextmanager
from fastapi import Depends, Request


class DataBase:
    __slots__ = ("__pool",)

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
    async def session(self) -> AsyncGenerator[asyncpg.Connection, None]:
        async with self.__pool.acquire() as conn:
            yield conn


async def get_session(r: Request):
    async with r.app.state.db_pool.session() as session:
        yield session


PostgresSession = Annotated[asyncpg.Connection, Depends(get_session)]
