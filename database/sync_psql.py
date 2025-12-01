import psycopg2
from configuration import PsqlConfig
from contextlib import contextmanager
from customlogger import LOGGER

class SyncPsql:

    __slots__ = '__conn'

    def __init__(self):
        self.__conn = psycopg2.connect(
            database=PsqlConfig.database,
            user=PsqlConfig.user,
            password=PsqlConfig.password,
            host=PsqlConfig.host,
            port=PsqlConfig.port
        )

    @contextmanager
    def __call__(self):
        try:
            with self.__conn.cursor() as cursor:
                yield cursor
            self.__conn.commit()
        except Exception as e:
            LOGGER.error(f"{type(e).__name__}: {e} ")
            self.__conn.rollback()

    def commit(self):
        self.__conn.commit()