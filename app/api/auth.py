import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import deps as app_deps
from app.config import get_settings
from app.core.security import create_access_token, verify_password
from app.crud.user import user_crud
from app.models.user import PasswordResetToken, User
from app.schemas.auth import LoginRequest, PasswordResetConfirm, PasswordResetRequest, Token
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services.email import email_service

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(app_deps.get_db)) -> User:
    existing_user = user_crud.get_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="E-mail já cadastrado")
    user = user_crud.create(db, user_in)
    return user


@router.post("/login", response_model=Token)
def login_user(
    login_in: LoginRequest,
    db: Session = Depends(app_deps.get_db),
) -> Token:
    user = user_crud.get_by_email(db, login_in.email)
    if not user or not verify_password(login_in.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(subject=str(user.id), expires_delta=access_token_expires)
    return Token(access_token=access_token)


@router.post("/token", response_model=Token)
def login_with_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(app_deps.get_db),
) -> Token:
    user = user_crud.get_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(subject=str(user.id), expires_delta=access_token_expires)
    return Token(access_token=access_token)


@router.post("/password/reset/request", status_code=status.HTTP_202_ACCEPTED)
def request_password_reset(
    reset_request: PasswordResetRequest,
    db: Session = Depends(app_deps.get_db),
) -> dict[str, str]:
    user = user_crud.get_by_email(db, reset_request.email)
    if not user:
        # Não revelar se o e-mail existe ou não
        return {"message": "Se o e-mail existir, enviaremos instruções"}
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=2)
    user_crud.create_reset_token(db, user, token, expires_at)
    reset_url = _build_reset_url(token)
    email_service.send_password_reset(reset_request.email, reset_url)
    return {"message": "Se o e-mail existir, enviaremos instruções"}


@router.post("/password/reset/confirm")
def confirm_password_reset(
    payload: PasswordResetConfirm,
    db: Session = Depends(app_deps.get_db),
) -> dict[str, str]:
    token_obj = (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.token == payload.token,
            PasswordResetToken.used.is_(False),
            PasswordResetToken.expires_at > datetime.utcnow(),
        )
        .first()
    )
    if token_obj is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido ou expirado")
    user = user_crud.get(db, token_obj.user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuário não encontrado")
    user_crud.update(db, user, UserUpdate(password=payload.new_password))
    token_obj.used = True
    db.add(token_obj)
    db.commit()
    return {"message": "Senha atualizada com sucesso"}


def _build_reset_url(token: str) -> str:
    base_url = settings.frontend_base_url or "http://localhost:8000/reset-password"
    return f"{base_url}?token={token}"
