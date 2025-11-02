from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import deps as app_deps
from app.api.deps import get_current_active_user
from app.crud.user import user_crud
from app.models.user import User
from app.schemas.user import UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_active_user)) -> User:
    return current_user


@router.patch("/me", response_model=UserRead)
def update_current_user(
    user_in: UserUpdate,
    db: Session = Depends(app_deps.get_db),
    current_user: User = Depends(get_current_active_user),
) -> User:
    updated_user = user_crud.update(db, current_user, user_in)
    return updated_user


@router.get("/", response_model=list[UserRead])
def list_users(
    db: Session = Depends(app_deps.get_db),
    _: User = Depends(get_current_active_user),
) -> list[User]:
    return db.query(User).order_by(User.created_at.desc()).limit(100).all()


@router.get("/{user_id}", response_model=UserRead)
def read_user(
    user_id: int,
    db: Session = Depends(app_deps.get_db),
    _: User = Depends(get_current_active_user),
) -> User:
    user = user_crud.get(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    return user
