from datetime import datetime

from sqlalchemy import Column, Date, DateTime, Integer, String, Text

from app.database import Base


class WasteCode(Base):
    __tablename__ = "waste_codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    classification = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class StorageCode(Base):
    __tablename__ = "storage_codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Transporter(Base):
    __tablename__ = "transporters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    license_number = Column(String(255), nullable=False)
    license_issue_date = Column(Date, nullable=True)
    license_expiry_date = Column(Date, nullable=True)
    license_pdf_path = Column(String(512), nullable=True)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Recipient(Base):
    __tablename__ = "recipients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    facility_type = Column(String(255), nullable=True)
    license_number = Column(String(255), nullable=False)
    license_issue_date = Column(Date, nullable=True)
    license_expiry_date = Column(Date, nullable=True)
    license_pdf_path = Column(String(512), nullable=True)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
