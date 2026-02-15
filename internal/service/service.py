from .user import UserService
from .flat import FlatService
from .report import ReportService
from .interface_service import IFlatService, IUserService, IReportService
from internal.repository import Repository

class Service:
    __slots__ = ('User', 'Flat', 'Report')

    def __init__(self, repo: Repository):
        self.User: IUserService = UserService(repo)
        self.Flat: IFlatService = FlatService(repo)
        self.Report: IReportService = ReportService(repo)