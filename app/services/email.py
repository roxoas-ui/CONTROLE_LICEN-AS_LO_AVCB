from __future__ import annotations

from typing import Iterable

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from app.config import get_settings


class EmailService:
    def __init__(self) -> None:
        settings = get_settings()
        self.api_key = settings.sendgrid_api_key
        self.sender = settings.sendgrid_sender_email
        self.enabled = bool(self.api_key and self.sender)

    def send_email(self, to_emails: Iterable[str], subject: str, html_content: str) -> None:
        if not self.enabled:
            return
        message = Mail(from_email=self.sender, to_emails=list(to_emails), subject=subject, html_content=html_content)
        client = SendGridAPIClient(self.api_key)
        try:
            client.send(message)
        except Exception:
            # FIXME: substituir por logging estruturado
            return

    def send_license_expiry_notification(self, emails: Iterable[str], license_name: str, days_left: int) -> None:
        subject = f"Licença {license_name} vence em {days_left} dia(s)"
        html_content = (
            f"<p>Olá,</p><p>A licença <strong>{license_name}</strong> expira em {days_left} dia(s)."  # noqa: S608
            " Favor verificar as condicionantes pendentes.</p>"
        )
        self.send_email(emails, subject, html_content)

    def send_condition_overdue_notification(self, emails: Iterable[str], condition_title: str, entity: str) -> None:
        subject = f"Condicionante '{condition_title}' atrasada"
        html_content = (
            f"<p>Olá,</p><p>A condicionante <strong>{condition_title}</strong> do {entity} está atrasada."  # noqa: S608
            " Atualize o status o quanto antes.</p>"
        )
        self.send_email(emails, subject, html_content)

    def send_password_reset(self, email: str, reset_url: str) -> None:
        subject = "Redefinição de senha"
        html_content = (
            "<p>Você solicitou a redefinição de senha.</p>"
            f"<p>Clique no link para definir uma nova senha: <a href='{reset_url}'>{reset_url}</a></p>"
        )
        self.send_email([email], subject, html_content)


email_service = EmailService()
