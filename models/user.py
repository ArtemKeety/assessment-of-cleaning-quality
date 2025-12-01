import uuid
from .base import Base
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, Index, ForeignKey, Text, DateTime


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, server_default='true')

    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    flats = relationship("Flat", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_user_status', login, postgresql_where=is_active == True),
    )

class Session(Base):
    __tablename__ = 'session'

    guid = Column(String(255), primary_key=True, default=lambda: str(uuid.uuid4()))
    date = Column(DateTime, nullable=False, default=datetime.utcnow)
    agent = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    # Relationships
    user = relationship("User", back_populates="sessions")
