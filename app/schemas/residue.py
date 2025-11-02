from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class WasteCodeBase(BaseModel):
    code: str
    description: str | None = None
    classification: str | None = None


class WasteCodeCreate(WasteCodeBase):
    pass


class WasteCodeUpdate(BaseModel):
    code: str | None = None
    description: str | None = None
    classification: str | None = None


class WasteCodeRead(WasteCodeBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StorageCodeBase(BaseModel):
    code: str
    description: str | None = None


class StorageCodeCreate(StorageCodeBase):
    pass


class StorageCodeUpdate(BaseModel):
    code: str | None = None
    description: str | None = None


class StorageCodeRead(StorageCodeBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TransporterBase(BaseModel):
    name: str
    license_number: str
    license_issue_date: date | None = None
    license_expiry_date: date | None = None
    contact_email: EmailStr | None = None
    contact_phone: str | None = None


class TransporterCreate(TransporterBase):
    pass


class TransporterUpdate(BaseModel):
    name: str | None = None
    license_number: str | None = None
    license_issue_date: date | None = None
    license_expiry_date: date | None = None
    contact_email: EmailStr | None = None
    contact_phone: str | None = None


class TransporterRead(TransporterBase):
    id: int
    license_pdf_path: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RecipientBase(BaseModel):
    name: str
    facility_type: str | None = None
    license_number: str
    license_issue_date: date | None = None
    license_expiry_date: date | None = None
    contact_email: EmailStr | None = None
    contact_phone: str | None = None


class RecipientCreate(RecipientBase):
    pass


class RecipientUpdate(BaseModel):
    name: str | None = None
    facility_type: str | None = None
    license_number: str | None = None
    license_issue_date: date | None = None
    license_expiry_date: date | None = None
    contact_email: EmailStr | None = None
    contact_phone: str | None = None


class RecipientRead(RecipientBase):
    id: int
    license_pdf_path: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
