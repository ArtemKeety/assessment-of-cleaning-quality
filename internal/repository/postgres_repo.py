import asyncpg
from internal.repository.postgres import UserRepo,FlatRepo,ReportRepo
from internal.repository.interface_repo import IReportRepo, IFlatRepo, IUserRepo

class Repository:

    __slots__ = 'conn','User', 'Flat', 'Report',

    def __init__(self, conn: asyncpg.Connection):
        self.conn = conn
        self.User: IUserRepo = UserRepo(conn)
        self.Flat: IFlatRepo = FlatRepo(conn)
        self.Report: IReportRepo = ReportRepo(conn)