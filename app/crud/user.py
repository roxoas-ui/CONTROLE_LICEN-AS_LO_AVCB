from datetime import datetime

from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.user import PasswordResetToken, User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser:
    def get(self, db: Session, user_id: int) -> User | None:
        return db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, db: Session, email: str) -> User | None:
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, obj_in: UserCreate) -> User:
        db_user = User(
            email=obj_in.email,
            full_name=obj_in.full_name,
            hashed_password=get_password_hash(obj_in.password),
            is_active=obj_in.is_active,
            is_superuser=obj_in.is_superuser,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def update(self, db: Session, db_user: User, obj_in: UserUpdate) -> User:
        data = obj_in.dict(exclude_unset=True)
        if "password" in data and data["password"]:
            db_user.hashed_password = get_password_hash(data.pop("password"))
        for field, value in data.items():
            setattr(db_user, field, value)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def create_reset_token(self, db: Session, user: User, token: str, expires_at: datetime) -> PasswordResetToken:
        reset_token = PasswordResetToken(user_id=user.id, token=token, expires_at=expires_at)
        db.add(reset_token)
        db.commit()
        db.refresh(reset_token)
        return reset_token


user_crud = CRUDUser()
