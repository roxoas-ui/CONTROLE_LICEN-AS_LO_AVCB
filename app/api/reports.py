from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app import deps as app_deps
from app.api.deps import get_current_active_user
from app.models.license import License
from app.models.user import User
from app.services.reports import pdf_report_service

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/licenses")
def generate_license_report(
    days_until_expiry: int | None = None,
    db: Session = Depends(app_deps.get_db),
    _: User = Depends(get_current_active_user),
) -> FileResponse:
    query = db.query(License)
    if days_until_expiry is not None:
        target_date = date.today() + timedelta(days=days_until_expiry)
        query = query.filter(License.expiry_date <= target_date)
    licenses = query.order_by(License.expiry_date.asc()).all()
    if not licenses:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhuma licença encontrada")
    entries = [
        {
            "name": license.name,
            "issuing_agency": license.issuing_agency,
            "expiry_date": license.expiry_date.isoformat() if license.expiry_date else "",
            "status": getattr(license.status, "value", license.status),
        }
        for license in licenses
    ]
    report_path = pdf_report_service.generate_license_expiry_report(entries)
    return FileResponse(path=report_path, media_type="application/pdf", filename=report_path.name)
