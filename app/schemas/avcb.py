from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.avcb import AvcbConditionStatus, AvcbStatus


class AvcbConditionBase(BaseModel):
    title: str
    description: str | None = None
    responsible: str | None = None
    due_date: date | None = None
    status: AvcbConditionStatus = AvcbConditionStatus.OPEN
    completion_notes: str | None = None
    completed_at: date | None = None


class AvcbConditionCreate(AvcbConditionBase):
    pass


class AvcbConditionUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    responsible: str | None = None
    due_date: date | None = None
    status: AvcbConditionStatus | None = None
    completion_notes: str | None = None
    completed_at: date | None = None


class AvcbConditionRead(AvcbConditionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AvcbBase(BaseModel):
    property_name: str
    property_address: str | None = None
    technical_responsible: str | None = None
    issue_date: date | None = None
    expiry_date: date
    status: AvcbStatus = AvcbStatus.PENDING
    notes: str | None = None


class AvcbCreate(AvcbBase):
    conditions: list[AvcbConditionCreate] | None = None


class AvcbUpdate(BaseModel):
    property_name: str | None = None
    property_address: str | None = None
    technical_responsible: str | None = None
    issue_date: date | None = None
    expiry_date: date | None = None
    status: AvcbStatus | None = None
    notes: str | None = None
    conditions: list[AvcbConditionUpdate] | None = None


class AvcbRead(AvcbBase):
    id: int
    pdf_path: str | None
    created_at: datetime
    updated_at: datetime
    conditions: list[AvcbConditionRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class AvcbNotificationRequest(BaseModel):
    emails: list[EmailStr]
    days_left: int
