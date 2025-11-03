"""Ferramentas de linha de comando para preparar a aplicação.

Uso básico:
    python scripts/bootstrap.py init-db
    python scripts/bootstrap.py create-superuser --email admin@example.com
"""

from __future__ import annotations

import argparse
from getpass import getpass

from sqlalchemy.exc import OperationalError

from app.crud.user import user_crud
from app.database import Base, SessionLocal, engine
from app.schemas.user import UserCreate


def init_db() -> None:
    """Cria as tabelas no banco configurado."""
    try:
        Base.metadata.create_all(bind=engine)
    except OperationalError as exc:
        raise SystemExit(f"Falha ao conectar ao banco de dados: {exc}") from exc
    print("Tabelas criadas/verificadas com sucesso.")


def create_superuser(email: str | None, full_name: str | None, password: str | None) -> None:
    """Cria um usuário administrador interativamente."""
    if not email:
        email = input("E-mail do administrador: ").strip()
    if not full_name:
        full_name = input("Nome completo: ").strip()
    if not password:
        password = _prompt_password()

    if not email or not full_name or not password:
        raise SystemExit("E-mail, nome e senha são obrigatórios.")

    session = SessionLocal()
    try:
        existing = user_crud.get_by_email(session, email)
        if existing:
            raise SystemExit("Já existe um usuário com este e-mail.")
        user_crud.create(
            session,
            UserCreate(
                email=email,
                full_name=full_name,
                password=password,
                is_active=True,
                is_superuser=True,
            ),
        )
        print("Superusuário criado com sucesso.")
    except OperationalError as exc:
        raise SystemExit(f"Falha ao conectar ao banco de dados: {exc}") from exc
    finally:
        session.close()


def _prompt_password() -> str:
    pwd = getpass("Senha: ")
    confirm = getpass("Confirme a senha: ")
    if pwd != confirm:
        raise SystemExit("As senhas não conferem.")
    if len(pwd) < 8:
        raise SystemExit("A senha deve ter pelo menos 8 caracteres.")
    return pwd


def main() -> None:
    parser = argparse.ArgumentParser(description="Utilitários de manutenção do sistema.")
    subcommands = parser.add_subparsers(dest="command", required=True)

    subcommands.add_parser("init-db", help="Cria as tabelas no banco configurado.")

    superuser_parser = subcommands.add_parser("create-superuser", help="Cria um usuário administrador.")
    superuser_parser.add_argument("--email", help="E-mail do administrador.")
    superuser_parser.add_argument("--full-name", help="Nome completo do administrador.")
    superuser_parser.add_argument("--password", help="Senha (será solicitada se omitida).")

    args = parser.parse_args()

    if args.command == "init-db":
        init_db()
    elif args.command == "create-superuser":
        create_superuser(args.email, args.full_name, args.password)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
