from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class AvcbStatus(str, PyEnum):
    VALID = "valid"
    EXPIRED = "expired"
    PENDING = "pending"
    SUSPENDED = "suspended"


class Avcb(Base):
    __tablename__ = "avcbs"

    id = Column(Integer, primary_key=True, index=True)
    property_name = Column(String(255), nullable=False)
    property_address = Column(Text, nullable=True)
    technical_responsible = Column(String(255), nullable=True)
    issue_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=False)
    status = Column(Enum(AvcbStatus), default=AvcbStatus.PENDING, nullable=False)
    notes = Column(Text, nullable=True)
    pdf_path = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    conditions = relationship(
        "AvcbCondition",
        back_populates="avcb",
        cascade="all, delete-orphan",
    )


class AvcbConditionStatus(str, PyEnum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"


class AvcbCondition(Base):
    __tablename__ = "avcb_conditions"

    id = Column(Integer, primary_key=True, index=True)
    avcb_id = Column(Integer, ForeignKey("avcbs.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    responsible = Column(String(255), nullable=True)
    due_date = Column(Date, nullable=True)
    status = Column(Enum(AvcbConditionStatus), default=AvcbConditionStatus.OPEN, nullable=False)
    completion_notes = Column(Text, nullable=True)
    completed_at = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    avcb = relationship("Avcb", back_populates="conditions")
