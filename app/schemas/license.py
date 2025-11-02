from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.license import ConditionStatus, LicenseStatus


class LicenseConditionBase(BaseModel):
    title: str
    description: str | None = None
    responsible: str | None = None
    due_date: date | None = None
    status: ConditionStatus = ConditionStatus.OPEN
    completion_notes: str | None = None
    completed_at: date | None = None


class LicenseConditionCreate(LicenseConditionBase):
    pass


class LicenseConditionUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    responsible: str | None = None
    due_date: date | None = None
    status: ConditionStatus | None = None
    completion_notes: str | None = None
    completed_at: date | None = None


class LicenseConditionRead(LicenseConditionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LicenseBase(BaseModel):
    name: str
    issuing_agency: str
    issue_date: date | None = None
    expiry_date: date
    status: LicenseStatus = LicenseStatus.PENDING
    notes: str | None = None


class LicenseCreate(LicenseBase):
    conditions: list[LicenseConditionCreate] | None = None


class LicenseUpdate(BaseModel):
    name: str | None = None
    issuing_agency: str | None = None
    issue_date: date | None = None
    expiry_date: date | None = None
    status: LicenseStatus | None = None
    notes: str | None = None
    conditions: list[LicenseConditionUpdate] | None = None


class LicenseRead(LicenseBase):
    id: int
    pdf_path: str | None
    created_at: datetime
    updated_at: datetime
    conditions: list[LicenseConditionRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class LicenseNotificationRequest(BaseModel):
    emails: list[EmailStr]
    days_left: int
