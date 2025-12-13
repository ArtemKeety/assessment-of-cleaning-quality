import pytest
from fastapi import FastAPI
from internal.midleware import get_header_data, user_identy
from database import RedisDb, DataBase


class FakeRedis:
    def __init__(self):
        self.deleted_keys = []

    async def delete(self, key: str):
        self.deleted_keys.append(key)


class TestAppFactory:
    def __init__(
        self,
        *,
        routers=None,              # один router или список
        fake_redis: FakeRedis | None = None,
        header_agent: str = "pytest-agent",
        session: str = "sess-123",
        user_id: int = 42,
        db_conn_factory=None,      # если надо вернуть не object()
    ):
        self.routers = routers
        self.fake_redis = fake_redis or FakeRedis()
        self.header_agent = header_agent
        self.session = session
        self.user_id = user_id
        self.db_conn_factory = db_conn_factory or (lambda: object())

    def build(self) -> FastAPI:
        app = FastAPI()

        if self.routers is not None:
            if isinstance(self.routers, (list, tuple)):
                for r in self.routers:
                    app.include_router(r)
            else:
                app.include_router(self.routers)

        # overrides
        async def override_get_header_data():
            return self.header_agent

        async def override_user_identy():
            return {"session": self.session, "user_id": self.user_id}

        async def override_db_conn():
            return self.db_conn_factory()

        async def override_redis_conn():
            return self.fake_redis

        app.dependency_overrides[get_header_data] = override_get_header_data
        app.dependency_overrides[user_identy] = override_user_identy
        app.dependency_overrides[DataBase.from_request_conn] = override_db_conn
        app.dependency_overrides[RedisDb.from_request_conn] = override_redis_conn

        return app




