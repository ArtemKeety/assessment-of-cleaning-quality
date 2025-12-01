from .base import Base
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index


class Report(Base):
    __tablename__ = 'report'

    id = Column(Integer, primary_key=True, index=True)
    flat_id = Column(Integer, ForeignKey('flat.id', ondelete='CASCADE'), nullable=False)
    preview = Column(String(255), nullable=False)
    date = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    flat = relationship("Flat", back_populates="reports")
    report_parts = relationship("ReportPart", back_populates="report", cascade="all, delete-orphan")

    __table_args__ = (
        Index('flat_for_report', flat_id),
    )


class ReportPart(Base):
    __tablename__ = 'report_part'

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey('report.id', ondelete='CASCADE'), nullable=False)
    info = Column(Text)
    path = Column(Text)

    # Relationships
    report = relationship("Report", back_populates="report_parts")

    __table_args__ = (
        Index('report_for_photo_report', report_id),
    )