from datetime import date

from sqlalchemy.orm import Session

from app.models.avcb import Avcb, AvcbCondition, AvcbConditionStatus
from app.schemas.avcb import (
    AvcbConditionCreate,
    AvcbConditionUpdate,
    AvcbCreate,
    AvcbUpdate,
)


class CRUDAvcb:
    def get(self, db: Session, avcb_id: int) -> Avcb | None:
        return db.query(Avcb).filter(Avcb.id == avcb_id).first()

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> list[Avcb]:
        return db.query(Avcb).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: AvcbCreate) -> Avcb:
        avcb = Avcb(
            property_name=obj_in.property_name,
            property_address=obj_in.property_address,
            technical_responsible=obj_in.technical_responsible,
            issue_date=obj_in.issue_date,
            expiry_date=obj_in.expiry_date,
            status=obj_in.status,
            notes=obj_in.notes,
        )
        if obj_in.conditions:
            for condition in obj_in.conditions:
                avcb.conditions.append(self._build_condition(condition))
        db.add(avcb)
        db.commit()
        db.refresh(avcb)
        return avcb

    def update(self, db: Session, db_obj: Avcb, obj_in: AvcbUpdate) -> Avcb:
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

    def remove(self, db: Session, avcb_id: int) -> Avcb:
        obj = self.get(db, avcb_id)
        if obj is None:
            raise ValueError("AVCB not found")
        db.delete(obj)
        db.commit()
        return obj

    def set_pdf_path(self, db: Session, avcb_obj: Avcb, path: str) -> Avcb:
        avcb_obj.pdf_path = path
        db.add(avcb_obj)
        db.commit()
        db.refresh(avcb_obj)
        return avcb_obj

    def mark_overdue_conditions(self, db: Session, current_date: date) -> None:
        overdue_conditions = (
            db.query(AvcbCondition)
            .filter(
                AvcbCondition.due_date.isnot(None),
                AvcbCondition.due_date < current_date,
                AvcbCondition.status != AvcbConditionStatus.COMPLETED,
            )
            .all()
        )
        for condition in overdue_conditions:
            condition.status = AvcbConditionStatus.OVERDUE
        if overdue_conditions:
            db.commit()

    def _build_condition(
        self, condition_schema: AvcbConditionCreate | AvcbConditionUpdate
    ) -> AvcbCondition:
        data = condition_schema.dict(exclude_unset=True)
        return AvcbCondition(**data)


avcb_crud = CRUDAvcb()
