from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class LicenseStatus(str, PyEnum):
    ACTIVE = "active"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    PENDING = "pending"


class License(Base):
    __tablename__ = "licenses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    issuing_agency = Column(String(255), nullable=False)
    issue_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=False)
    status = Column(Enum(LicenseStatus), default=LicenseStatus.PENDING, nullable=False)
    notes = Column(Text, nullable=True)
    pdf_path = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    conditions = relationship(
        "LicenseCondition",
        back_populates="license",
        cascade="all, delete-orphan",
    )


class ConditionStatus(str, PyEnum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"


class LicenseCondition(Base):
    __tablename__ = "license_conditions"

    id = Column(Integer, primary_key=True, index=True)
    license_id = Column(Integer, ForeignKey("licenses.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    responsible = Column(String(255), nullable=True)
    due_date = Column(Date, nullable=True)
    status = Column(Enum(ConditionStatus), default=ConditionStatus.OPEN, nullable=False)
    completion_notes = Column(Text, nullable=True)
    completed_at = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    license = relationship("License", back_populates="conditions")
