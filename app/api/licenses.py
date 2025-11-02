from datetime import date, timedelta

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app import deps as app_deps
from app.api.deps import get_current_active_user
from app.crud.license import license_crud
from app.models.license import License, LicenseStatus
from app.models.user import User
from app.schemas.license import (
    LicenseCreate,
    LicenseNotificationRequest,
    LicenseRead,
    LicenseUpdate,
)
from app.services.email import email_service
from app.utils.file_storage import save_upload

router = APIRouter(prefix="/licenses", tags=["licenses"])


@router.get("/", response_model=list[LicenseRead])
def list_licenses(
    status_filter: str | None = None,
    days_until_expiry: int | None = None,
    db: Session = Depends(app_deps.get_db),
    _: User = Depends(get_current_active_user),
) -> list[License]:
    query = db.query(License)
    if status_filter:
        try:
            status_enum = LicenseStatus(status_filter)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Status inválido") from exc
        query = query.filter(License.status == status_enum)
    if days_until_expiry is not None:
        target_date = date.today() + timedelta(days=days_until_expiry)
        query = query.filter(License.expiry_date <= target_date)
    license_crud.mark_overdue_conditions(db, date.today())
    return query.order_by(License.expiry_date.asc()).all()


@router.post("/", response_model=LicenseRead, status_code=status.HTTP_201_CREATED)
def create_license(
    license_in: LicenseCreate,
    db: Session = Depends(app_deps.get_db),
    _: User = Depends(get_current_active_user),
) -> License:
    return license_crud.create(db, license_in)


@router.get("/{license_id}", response_model=LicenseRead)
def read_license(
    license_id: int,
    db: Session = Depends(app_deps.get_db),
    _: User = Depends(get_current_active_user),
) -> License:
    license_obj = license_crud.get(db, license_id)
    if license_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Licença não encontrada")
    return license_obj


@router.put("/{license_id}", response_model=LicenseRead)
@router.patch("/{license_id}", response_model=LicenseRead)
def update_license(
    license_id: int,
    license_in: LicenseUpdate,
    db: Session = Depends(app_deps.get_db),
    _: User = Depends(get_current_active_user),
) -> License:
    license_obj = license_crud.get(db, license_id)
    if license_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Licença não encontrada")
    return license_crud.update(db, license_obj, license_in)


@router.delete("/{license_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_license(
    license_id: int,
    db: Session = Depends(app_deps.get_db),
    _: User = Depends(get_current_active_user),
) -> None:
    license_obj = license_crud.get(db, license_id)
    if license_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Licença não encontrada")
    license_crud.remove(db, license_id)


@router.post("/{license_id}/upload", response_model=LicenseRead)
def upload_license_pdf(
    license_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(app_deps.get_db),
    _: User = Depends(get_current_active_user),
) -> License:
    license_obj = license_crud.get(db, license_id)
    if license_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Licença não encontrada")
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Envie um arquivo PDF")
    path = save_upload(file, "licenses")
    return license_crud.set_pdf_path(db, license_obj, path)


@router.get("/{license_id}/download")
def download_license_pdf(
    license_id: int,
    db: Session = Depends(app_deps.get_db),
    _: User = Depends(get_current_active_user),
) -> FileResponse:
    license_obj = license_crud.get(db, license_id)
    if license_obj is None or not license_obj.pdf_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento não encontrado")
    return FileResponse(path=license_obj.pdf_path, media_type="application/pdf", filename=f"licenca_{license_id}.pdf")


@router.post("/{license_id}/notify")
def notify_license_expiry(
    license_id: int,
    payload: LicenseNotificationRequest,
    db: Session = Depends(app_deps.get_db),
    _: User = Depends(get_current_active_user),
) -> dict[str, str]:
    license_obj = license_crud.get(db, license_id)
    if license_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Licença não encontrada")
    email_service.send_license_expiry_notification(payload.emails, license_obj.name, payload.days_left)
    return {"status": "ok"}
