from .base import Base
from datetime import datetime


class Report(Base):
    id: int
    flat_id: int
    preview: str
    date: datetime


class ReportPath(Base):
    id: int
    report_id: int
    info: str
    path: str

