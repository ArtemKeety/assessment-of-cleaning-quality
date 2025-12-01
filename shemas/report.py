from .base import Base
from datetime import datetime

class BaseReport(Base):
    flat_id: int
    preview: str
    date: datetime

class Report(BaseReport):
    id: int


class ReportPath(Base):
    id: int
    report_id: int
    info: str
    path: str

