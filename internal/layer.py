
from fastapi import Request
from utils import TransactionEnum
from internal.service import Service
from dataclasses import dataclass, field
from internal.repository import Repository

from typing import Protocol, Any, AsyncGenerator
from contextlib import AbstractAsyncContextManager, asynccontextmanager


class IDatabase(Protocol):

    @asynccontextmanager
    def session(self) -> AbstractAsyncContextManager[Any]:
        ...
    @asynccontextmanager
    def transaction(self, tr: TransactionEnum)-> AbstractAsyncContextManager[Any]:
        ...


@dataclass(frozen=True, init=True, slots=True)
class Layer:
    tr: TransactionEnum = field(default=TransactionEnum.read_committed)

    async def __call__(self, request: Request) -> AsyncGenerator[Service, Any]:
        db: IDatabase = request.app.state.db_pool
        async with db.transaction(self.tr) as session:
            repo = Repository(session)
            service = Service(repo)
            yield service

