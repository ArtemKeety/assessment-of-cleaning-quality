from .user import UserService
from .flat import FlatService
from .report import ReportService
from internal.repository import Repository
from .interface_service import IFlatService, IUserService, IReportService

class Service:
    __slots__ = ('User', 'Flat', 'Report')

    def __init__(self, repo: Repository):
        self.User: IUserService = UserService(repo)
        self.Flat: IFlatService = FlatService(repo)
        self.Report: IReportService = ReportService(repo)