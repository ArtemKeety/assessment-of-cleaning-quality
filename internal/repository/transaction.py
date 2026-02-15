from typing import Optional
from customlogger import LOGGER
from asyncpg import transaction
from .interface_repo import IRepository
from utils.isolation_lvl import IsolationLvl



class Transaction:

    __slots__ = ('repo', 'tr', 'iso_lvl')

    def __init__(self, repo: IRepository, iso_lvl: IsolationLvl = IsolationLvl.read_committed):
        self.repo: IRepository = repo
        self.tr: Optional[transaction.Transaction] = None
        self.iso_lvl = iso_lvl

    async def __aenter__(self)-> 'IRepository':
        self.tr = self.repo.conn.transaction(isolation=self.iso_lvl)
        await self.tr.start()
        return self.repo

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is None:
                await self.tr.commit()
            else:
                await self.tr.rollback()
        except Exception as e:
            LOGGER.warning(f"{type(e).__name__}: {e}")