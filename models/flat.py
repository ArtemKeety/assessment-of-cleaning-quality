from .base import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Text, Index



class Flat(Base):
    __tablename__ = 'flat'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(255), nullable=False)
    preview = Column(String(255), nullable=False)

    # Relationships
    user = relationship("User", back_populates="flats")
    photos = relationship("Photo", back_populates="flat", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="flat", cascade="all, delete-orphan")

    __table_args__ = (
        Index('user_id_for_flat', user_id),
    )


class Photo(Base):
    __tablename__ = 'photo'

    id = Column(Integer, primary_key=True, autoincrement=True)
    path = Column(Text, nullable=False)
    flat_id = Column(Integer, ForeignKey('flat.id', ondelete='CASCADE'), nullable=False)

    # Relationships
    flat = relationship("Flat", back_populates="photos")

    __table_args__ = (
        Index('flat_for_photo', flat_id),
    )