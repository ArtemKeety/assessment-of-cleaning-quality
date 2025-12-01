from .base import Base


class Flat(Base):
    id: int
    preview : str
    name: str


class FullFlat(Base):
    id: int
    path: str
