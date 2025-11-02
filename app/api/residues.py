from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app import deps as app_deps
from app.api.deps import get_current_active_user
from app.crud.residue import (
    recipient_crud,
    storage_code_crud,
    transporter_crud,
    waste_code_crud,
)
from app.models.residue import Recipient, StorageCode, Transporter, WasteCode
from app.models.user import User
from app.schemas.residue import (
    RecipientCreate,
    RecipientRead,
    RecipientUpdate,
    StorageCodeCreate,
    StorageCodeRead,
    StorageCodeUpdate,
    TransporterCreate,
    TransporterRead,
    TransporterUpdate,
    WasteCodeCreate,
    WasteCodeRead,
    WasteCodeUpdate,
)
from app.utils.file_storage import save_upload

router = APIRouter(prefix="/residues", tags=["residues"])


# Waste Codes
@router.get("/codes", response_model=list[WasteCodeRead])
def list_waste_codes(
    db: Session = Depends(app_deps.get_db),
    _: User = Depends(get_current_active_user),
) -> list[WasteCode]:
    return waste_code_crud.get_multi(db)


@router.post("/codes", response_model=WasteCodeRead, status_code=status.HTTP_201_CREATED)
def create_waste_code(
    payload: WasteCodeCreate,
    db: Session = Depends(app_deps.get_db),
    _: User = Depends(get_current_active_user),
) -> WasteCode:
    return waste_code_crud.create(db, payload)


@router.patch("/codes/{code_id}", response_model=WasteCodeRead)
def update_waste_code(
    code_id: int,
    payload: WasteCodeUpdate,
    db: Session = Depends(app_deps.get_db),
    _: User = Depends(get_current_active_user),
) -> WasteCode:
    db_obj = waste_code_crud.get(db, code_id)
    if db_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Código não encontrado")
    return waste_code_crud.update(db, db_obj, payload)


@router.delete("/codes/{code_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_waste_code(
    code_id: int,
    db: Session = Depends(app_deps.get_db),
    _: User = Depends(get_current_active_user),
) -> None:
    db_obj = waste_code_crud.get(db, code_id)
    if db_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Código não encontrado")
    waste_code_crud.remove(db, code_id)


# Storage Codes
@router.get("/storage", response_model=list[StorageCodeRead])
def list_storage_codes(
    db: Session = Depends(app_deps.get_db),
    _: User = Depends(get_current_active_user),
) -> list[StorageCode]:
    return storage_code_crud.get_multi(db)


@router.post("/storage", response_model=StorageCodeRead, status_code=status.HTTP_201_CREATED)
def create_storage_code(
    payload: StorageCodeCreate,
    db: Session = Depends(app_deps.get_db),
    _: User = Depends(get_current_active_user),
) -> StorageCode:
    return storage_code_crud.create(db, payload)


@router.patch("/storage/{storage_id}", response_model=StorageCodeRead)
def update_storage_code(
    storage_id: int,
    payload: StorageCodeUpdate,
    db: Session = Depends(app_deps.get_db),
    _: User = Depends(get_current_active_user),
) -> StorageCode:
    db_obj = storage_code_crud.get(db, storage_id)
    if db_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Código não encontrado")
    return storage_code_crud.update(db, db_obj, payload)


@router.delete("/storage/{storage_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_storage_code(
    storage_id: int,
    db: Session = Depends(app_deps.get_db),
    _: User = Depends(get_current_active_user),
) -> None:
    db_obj = storage_code_crud.get(db, storage_id)
    if db_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Código não encontrado")
    storage_code_crud.remove(db, storage_id)


# Transporters
@router.get("/transporters", response_model=list[TransporterRead])
def list_transporters(
    db: Session = Depends(app_deps.get_db),
    _: User = Depends(get_current_active_user),
) -> list[Transporter]:
    return transporter_crud.get_multi(db)


@router.post("/transporters", response_model=TransporterRead, status_code=status.HTTP_201_CREATED)
def create_transporter(
    payload: TransporterCreate,
    db: Session = Depends(app_deps.get_db),
    _: User = Depends(get_current_active_user),
) -> Transporter:
    return transporter_crud.create(db, payload)


@router.patch("/transporters/{transporter_id}", response_model=TransporterRead)
def update_transporter(
    transporter_id: int,
    payload: TransporterUpdate,
    db: Session = Depends(app_deps.get_db),
    _: User = Depends(get_current_active_user),
) -> Transporter:
    db_obj = transporter_crud.get(db, transporter_id)
    if db_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transportador não encontrado")
    return transporter_crud.update(db, db_obj, payload)


@router.delete("/transporters/{transporter_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transporter(
    transporter_id: int,
    db: Session = Depends(app_deps.get_db),
    _: User = Depends(get_current_active_user),
) -> None:
    db_obj = transporter_crud.get(db, transporter_id)
    if db_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transportador não encontrado")
    transporter_crud.remove(db, transporter_id)


@router.post("/transporters/{transporter_id}/upload", response_model=TransporterRead)
def upload_transporter_license(
    transporter_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(app_deps.get_db),
    _: User = Depends(get_current_active_user),
) -> Transporter:
    db_obj = transporter_crud.get(db, transporter_id)
    if db_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transportador não encontrado")
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Envie um arquivo PDF")
    path = save_upload(file, "transporters")
    return transporter_crud.set_pdf_path(db, db_obj, path)


# Recipients
@router.get("/recipients", response_model=list[RecipientRead])
def list_recipients(
    db: Session = Depends(app_deps.get_db),
    _: User = Depends(get_current_active_user),
) -> list[Recipient]:
    return recipient_crud.get_multi(db)


@router.post("/recipients", response_model=RecipientRead, status_code=status.HTTP_201_CREATED)
def create_recipient(
    payload: RecipientCreate,
    db: Session = Depends(app_deps.get_db),
    _: User = Depends(get_current_active_user),
) -> Recipient:
    return recipient_crud.create(db, payload)


@router.patch("/recipients/{recipient_id}", response_model=RecipientRead)
def update_recipient(
    recipient_id: int,
    payload: RecipientUpdate,
    db: Session = Depends(app_deps.get_db),
    _: User = Depends(get_current_active_user),
) -> Recipient:
    db_obj = recipient_crud.get(db, recipient_id)
    if db_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Destinatário não encontrado")
    return recipient_crud.update(db, db_obj, payload)


@router.delete("/recipients/{recipient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipient(
    recipient_id: int,
    db: Session = Depends(app_deps.get_db),
    _: User = Depends(get_current_active_user),
) -> None:
    db_obj = recipient_crud.get(db, recipient_id)
    if db_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Destinatário não encontrado")
    recipient_crud.remove(db, recipient_id)


@router.post("/recipients/{recipient_id}/upload", response_model=RecipientRead)
def upload_recipient_license(
    recipient_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(app_deps.get_db),
    _: User = Depends(get_current_active_user),
) -> Recipient:
    db_obj = recipient_crud.get(db, recipient_id)
    if db_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Destinatário não encontrado")
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Envie um arquivo PDF")
    path = save_upload(file, "recipients")
    return recipient_crud.set_pdf_path(db, db_obj, path)
