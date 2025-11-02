from datetime import date

from sqlalchemy.orm import Session

from app.models.license import ConditionStatus, License, LicenseCondition
from app.schemas.license import (
    LicenseConditionCreate,
    LicenseConditionUpdate,
    LicenseCreate,
    LicenseUpdate,
)


class CRUDLicense:
    def get(self, db: Session, license_id: int) -> License | None:
        return db.query(License).filter(License.id == license_id).first()

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> list[License]:
        return db.query(License).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: LicenseCreate) -> License:
        license_obj = License(
            name=obj_in.name,
            issuing_agency=obj_in.issuing_agency,
            issue_date=obj_in.issue_date,
            expiry_date=obj_in.expiry_date,
            status=obj_in.status,
            notes=obj_in.notes,
        )
        if obj_in.conditions:
            for condition in obj_in.conditions:
                license_obj.conditions.append(self._build_condition(condition))
        db.add(license_obj)
        db.commit()
        db.refresh(license_obj)
        return license_obj

    def update(self, db: Session, db_obj: License, obj_in: LicenseUpdate) -> License:
        data = obj_in.dict(exclude_unset=True)
        conditions_data = data.pop("conditions", None)
        for field, value in data.items():
            setattr(db_obj, field, value)
        if conditions_data is not None:
            db_obj.conditions.clear()
            for condition in conditions_data:
                db_obj.conditions.append(self._build_condition(condition))
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, license_id: int) -> License:
        obj = self.get(db, license_id)
        if obj is None:
            raise ValueError("License not found")
        db.delete(obj)
        db.commit()
        return obj

    def set_pdf_path(self, db: Session, license_obj: License, path: str) -> License:
        license_obj.pdf_path = path
        db.add(license_obj)
        db.commit()
        db.refresh(license_obj)
        return license_obj

    def mark_overdue_conditions(self, db: Session, current_date: date) -> None:
        overdue_conditions = (
            db.query(LicenseCondition)
            .filter(
                LicenseCondition.due_date.isnot(None),
                LicenseCondition.due_date < current_date,
                LicenseCondition.status != ConditionStatus.COMPLETED,
            )
            .all()
        )
        for condition in overdue_conditions:
            condition.status = ConditionStatus.OVERDUE
        if overdue_conditions:
            db.commit()

    def _build_condition(self, condition_schema: LicenseConditionCreate | LicenseConditionUpdate) -> LicenseCondition:
        data = condition_schema.dict(exclude_unset=True)
        return LicenseCondition(**data)


license_crud = CRUDLicense()
