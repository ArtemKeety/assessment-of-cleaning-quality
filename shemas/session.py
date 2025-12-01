from .base import Base
from pydantic import Field

class Session(Base):
    session: str = Field(min_length=3, max_length=255)

