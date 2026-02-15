from .base import Base
from pydantic import Field

class Pagination(Base):
    page: int = Field(default=1, gt=0)
    volume: int = Field(default=100, gt=0)

    @property
    def limit(self) -> int:
        return self.volume

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.volume
