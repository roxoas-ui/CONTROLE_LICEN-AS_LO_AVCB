from datetime import date, timedelta

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app import deps as app_deps
from app.api.deps import get_current_active_user
from app.crud.avcb import avcb_crud
from app.models.avcb import Avcb, AvcbStatus
from app.models.user import User
from app.schemas.avcb import AvcbCreate, AvcbNotificationRequest, AvcbRead, AvcbUpdate
from app.services.email import email_service
from app.utils.file_storage import save_upload

router = APIRouter(prefix="/avcb", tags=["avcb"])


@router.get("/", response_model=list[AvcbRead])
def list_avcb(
    status_filter: str | None = None,
    days_until_expiry: int | None = None,
    db: Session = Depends(app_deps.get_db),
    _: User = Depends(get_current_active_user),
) -> list[Avcb]:
    query = db.query(Avcb)
    if status_filter:
        try:
            status_enum = AvcbStatus(status_filter)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Status inválido") from exc
        query = query.filter(Avcb.status == status_enum)
    if days_until_expiry is not None:
        target_date = date.today() + timedelta(days=days_until_expiry)
        query = query.filter(Avcb.expiry_date <= target_date)
    avcb_crud.mark_overdue_conditions(db, date.today())
    return query.order_by(Avcb.expiry_date.asc()).all()


@router.post("/", response_model=AvcbRead, status_code=status.HTTP_201_CREATED)
def create_avcb(
    avcb_in: AvcbCreate,
    db: Session = Depends(app_deps.get_db),
    _: User = Depends(get_current_active_user),
) -> Avcb:
    return avcb_crud.create(db, avcb_in)


@router.get("/{avcb_id}", response_model=AvcbRead)
def read_avcb(
    avcb_id: int,
    db: Session = Depends(app_deps.get_db),
    _: User = Depends(get_current_active_user),
) -> Avcb:
    avcb_obj = avcb_crud.get(db, avcb_id)
    if avcb_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AVCB não encontrado")
    return avcb_obj


@router.put("/{avcb_id}", response_model=AvcbRead)
@router.patch("/{avcb_id}", response_model=AvcbRead)
def update_avcb(
    avcb_id: int,
    avcb_in: AvcbUpdate,
    db: Session = Depends(app_deps.get_db),
    _: User = Depends(get_current_active_user),
) -> Avcb:
    avcb_obj = avcb_crud.get(db, avcb_id)
    if avcb_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AVCB não encontrado")
    return avcb_crud.update(db, avcb_obj, avcb_in)


@router.delete("/{avcb_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_avcb(
    avcb_id: int,
    db: Session = Depends(app_deps.get_db),
    _: User = Depends(get_current_active_user),
) -> None:
    avcb_obj = avcb_crud.get(db, avcb_id)
    if avcb_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AVCB não encontrado")
    avcb_crud.remove(db, avcb_id)


@router.post("/{avcb_id}/upload", response_model=AvcbRead)
def upload_avcb_pdf(
    avcb_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(app_deps.get_db),
    _: User = Depends(get_current_active_user),
) -> Avcb:
    avcb_obj = avcb_crud.get(db, avcb_id)
    if avcb_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AVCB não encontrado")
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Envie um arquivo PDF")
    path = save_upload(file, "avcb")
    return avcb_crud.set_pdf_path(db, avcb_obj, path)


@router.get("/{avcb_id}/download")
def download_avcb_pdf(
    avcb_id: int,
    db: Session = Depends(app_deps.get_db),
    _: User = Depends(get_current_active_user),
) -> FileResponse:
    avcb_obj = avcb_crud.get(db, avcb_id)
    if avcb_obj is None or not avcb_obj.pdf_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento não encontrado")
    return FileResponse(path=avcb_obj.pdf_path, media_type="application/pdf", filename=f"avcb_{avcb_id}.pdf")


@router.post("/{avcb_id}/notify")
def notify_avcb_expiry(
    avcb_id: int,
    payload: AvcbNotificationRequest,
    db: Session = Depends(app_deps.get_db),
    _: User = Depends(get_current_active_user),
) -> dict[str, str]:
    avcb_obj = avcb_crud.get(db, avcb_id)
    if avcb_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AVCB não encontrado")
    email_service.send_license_expiry_notification(payload.emails, avcb_obj.property_name, payload.days_left)
    return {"status": "ok"}
