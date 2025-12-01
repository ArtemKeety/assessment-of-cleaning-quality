import asyncpg
from fastapi import Request
from customlogger import LOGGER
from configuration import PsqlConfig
from contextlib import asynccontextmanager

class DataBase:

    __slots__ = '__pool'

    def __init__(self):
        self.__pool: asyncpg.Pool = None

    async def __create_pool(self):
        self.__pool = await asyncpg.create_pool(
            host=PsqlConfig.host,
            port=PsqlConfig.port,
            user=PsqlConfig.user,
            password=PsqlConfig.password,
            database=PsqlConfig.database,
            timeout=PsqlConfig.timeout,
            max_size=PsqlConfig.max_size,
            min_size=PsqlConfig.min_size,
        )

    @classmethod
    async def connect(cls)-> 'DataBase':
        obj = cls()
        await obj.__create_pool()
        LOGGER.info("Connected to database")
        return obj

    async def disconnect(self):
        await self.__pool.close()
        LOGGER.info("Disconnected to database")

    @asynccontextmanager
    async def __call__(self) -> asyncpg.Connection:
        async with self.__pool.acquire() as connection:
            yield connection

    async def test_conn(self):
        async with self() as conn:
            await conn.execute('SELECT 1')

    @staticmethod
    async def from_request_conn(request: Request) -> asyncpg.Connection:
        async with request.app.state.db_pool() as conn:
            yield conn

    @staticmethod
    async def from_request_pool(request: Request) -> 'DataBase':
        return request.app.state.db_pool


