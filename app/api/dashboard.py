from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import deps as app_deps
from app.api.deps import get_current_active_user
from app.models.avcb import Avcb
from app.models.license import License
from app.models.residue import Recipient, Transporter, WasteCode
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/")
def get_dashboard_stats(
    db: Session = Depends(app_deps.get_db),
    _: User = Depends(get_current_active_user),
) -> dict[str, int]:
    today = date.today()
    upcoming_threshold = today + timedelta(days=30)
    return {
        "licenses_total": db.query(func.count(License.id)).scalar() or 0,
        "licenses_expiring_30": (
            db.query(func.count(License.id))
            .filter(License.expiry_date <= upcoming_threshold)
            .scalar()
            or 0
        ),
        "avcb_total": db.query(func.count(Avcb.id)).scalar() or 0,
        "avcb_expiring_30": (
            db.query(func.count(Avcb.id)).filter(Avcb.expiry_date <= upcoming_threshold).scalar() or 0
        ),
        "waste_codes_total": db.query(func.count(WasteCode.id)).scalar() or 0,
        "transporters_total": db.query(func.count(Transporter.id)).scalar() or 0,
        "recipients_total": db.query(func.count(Recipient.id)).scalar() or 0,
    }
