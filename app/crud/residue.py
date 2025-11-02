from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.residue import Recipient, StorageCode, Transporter, WasteCode
from app.schemas.residue import (
    RecipientCreate,
    RecipientUpdate,
    StorageCodeCreate,
    StorageCodeUpdate,
    TransporterCreate,
    TransporterUpdate,
    WasteCodeCreate,
    WasteCodeUpdate,
)


class CRUDWasteCode(CRUDBase[WasteCode, WasteCodeCreate, WasteCodeUpdate]):
    pass


class CRUDStorageCode(CRUDBase[StorageCode, StorageCodeCreate, StorageCodeUpdate]):
    pass


class CRUDTransporter(CRUDBase[Transporter, TransporterCreate, TransporterUpdate]):
    def set_pdf_path(self, db: Session, db_obj: Transporter, path: str) -> Transporter:
        db_obj.license_pdf_path = path
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


class CRUDRecipient(CRUDBase[Recipient, RecipientCreate, RecipientUpdate]):
    def set_pdf_path(self, db: Session, db_obj: Recipient, path: str) -> Recipient:
        db_obj.license_pdf_path = path
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


waste_code_crud = CRUDWasteCode(WasteCode)
storage_code_crud = CRUDStorageCode(StorageCode)
transporter_crud = CRUDTransporter(Transporter)
recipient_crud = CRUDRecipient(Recipient)
