from datetime import date, timedelta
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import deps
from app.crud.residue import recipient_crud, transporter_crud, waste_code_crud
from app.models import Avcb, AvcbStatus, License, LicenseStatus, Recipient, Transporter, WasteCode
from app.schemas.residue import (
    RecipientCreate,
    RecipientUpdate,
    TransporterCreate,
    TransporterUpdate,
    WasteCodeCreate,
    WasteCodeUpdate,
)

router = APIRouter(tags=["frontend"])
templates = Jinja2Templates(directory="app/templates")


def _clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def _parse_optional_int(value: str | None, field_label: str) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_label} inválido.") from exc


def _parse_optional_date(value: str | None, field_label: str) -> date | None:
    if value is None or value == "":
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field_label} inválida.") from exc

def _redirect_with_feedback(request: Request, *, message: str | None = None, error: str | None = None) -> RedirectResponse:
    params: dict[str, str] = {}
    if message:
        params["message"] = message
    if error:
        params["error"] = error
    url = request.url_for("list_residues")
    if params:
        url = f"{url}?{urlencode(params)}"
    return RedirectResponse(url, status_code=status.HTTP_303_SEE_OTHER)


def _format_validation_errors(exc: ValidationError) -> str:
    return ", ".join(err.get("msg", "Dados inválidos.") for err in exc.errors())


@router.get("/ui/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(deps.get_db)) -> HTMLResponse:
    today = date.today()
    licenses_total = db.query(License).count()
    licenses_expiring = db.query(License).filter(License.expiry_date <= today).count()
    avcb_total = db.query(Avcb).count()
    avcb_expiring = db.query(Avcb).filter(Avcb.expiry_date <= today).count()
    waste_codes_total = db.query(WasteCode).count()
    transporters_total = db.query(Transporter).count()
    recipients_total = db.query(Recipient).count()
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "metrics": {
                "licenses_total": licenses_total,
                "licenses_expiring": licenses_expiring,
                "avcb_total": avcb_total,
                "avcb_expiring": avcb_expiring,
                "waste_codes_total": waste_codes_total,
                "transporters_total": transporters_total,
                "recipients_total": recipients_total,
            },
        },
    )


@router.get("/ui/licenses", response_class=HTMLResponse)
async def list_licenses(request: Request, db: Session = Depends(deps.get_db)) -> HTMLResponse:
    query = db.query(License).order_by(License.expiry_date.asc())
    status_param = _clean_text(request.query_params.get("status"))
    due_within_param = _clean_text(request.query_params.get("due_within"))
    today = date.today()

    selected_status: str | None = None
    selected_due_within: int | None = None

    if status_param:
        try:
            status_value = LicenseStatus(status_param)
        except ValueError:
            status_value = None
        if status_value:
            query = query.filter(License.status == status_value)
            selected_status = status_value.value

    if due_within_param:
        try:
            selected_due_within = int(due_within_param)
            deadline = today + timedelta(days=selected_due_within)
            query = query.filter(License.expiry_date <= deadline)
        except ValueError:
            selected_due_within = None

    licenses = query.limit(100).all()
    return templates.TemplateResponse(
        "licenses.html",
        {
            "request": request,
            "licenses": licenses,
            "license_status_options": [(status.value, status.name.replace("_", " ").title()) for status in LicenseStatus],
            "due_within_options": [30, 60, 90, 180],
            "selected_status": selected_status,
            "selected_due_within": selected_due_within,
        },
    )


@router.get("/ui/avcbs", response_class=HTMLResponse)
async def list_avcbs(request: Request, db: Session = Depends(deps.get_db)) -> HTMLResponse:
    query = db.query(Avcb).order_by(Avcb.expiry_date.asc())
    status_param = _clean_text(request.query_params.get("status"))
    due_within_param = _clean_text(request.query_params.get("due_within"))
    today = date.today()

    selected_status: str | None = None
    selected_due_within: int | None = None

    if status_param:
        try:
            status_value = AvcbStatus(status_param)
        except ValueError:
            status_value = None
        if status_value:
            query = query.filter(Avcb.status == status_value)
            selected_status = status_value.value

    if due_within_param:
        try:
            selected_due_within = int(due_within_param)
            deadline = today + timedelta(days=selected_due_within)
            query = query.filter(Avcb.expiry_date <= deadline)
        except ValueError:
            selected_due_within = None

    avcbs = query.limit(100).all()
    return templates.TemplateResponse(
        "avcbs.html",
        {
            "request": request,
            "avcbs": avcbs,
            "avcb_status_options": [(status.value, status.name.replace("_", " ").title()) for status in AvcbStatus],
            "due_within_options": [30, 60, 90, 180],
            "selected_status": selected_status,
            "selected_due_within": selected_due_within,
        },
    )


@router.get("/ui/residues", response_class=HTMLResponse)
async def list_residues(request: Request, db: Session = Depends(deps.get_db)) -> HTMLResponse:
    waste_codes = db.query(WasteCode).order_by(WasteCode.code.asc()).all()
    transporters = db.query(Transporter).order_by(Transporter.name.asc()).all()
    recipients = db.query(Recipient).order_by(Recipient.name.asc()).all()
    edit_waste_code: WasteCode | None = None
    edit_transporter: Transporter | None = None
    edit_recipient: Recipient | None = None

    try:
        edit_waste_code_id = _parse_optional_int(request.query_params.get("edit_waste_code"), "Código")
        if edit_waste_code_id:
            edit_waste_code = waste_code_crud.get(db, edit_waste_code_id)
    except ValueError:
        edit_waste_code = None

    try:
        edit_transporter_id = _parse_optional_int(request.query_params.get("edit_transporter"), "Transportadora")
        if edit_transporter_id:
            edit_transporter = transporter_crud.get(db, edit_transporter_id)
    except ValueError:
        edit_transporter = None

    try:
        edit_recipient_id = _parse_optional_int(request.query_params.get("edit_recipient"), "Destinatário")
        if edit_recipient_id:
            edit_recipient = recipient_crud.get(db, edit_recipient_id)
    except ValueError:
        edit_recipient = None
    return templates.TemplateResponse(
        "residues.html",
        {
            "request": request,
            "waste_codes": waste_codes,
            "transporters": transporters,
            "recipients": recipients,
            "message": request.query_params.get("message"),
            "error": request.query_params.get("error"),
            "edit_waste_code": edit_waste_code,
            "edit_transporter": edit_transporter,
            "edit_recipient": edit_recipient,
        },
    )


@router.post("/ui/residues/waste-codes", response_class=HTMLResponse)
async def create_waste_code_form(
    request: Request,
    code_id: str | None = Form(None),
    code: str = Form(...),
    classification: str | None = Form(None),
    description: str | None = Form(None),
    db: Session = Depends(deps.get_db),
) -> RedirectResponse:
    code_clean = _clean_text(code)
    if not code_clean:
        return _redirect_with_feedback(request, error="Informe o código do resíduo.")

    try:
        code_id_value = _parse_optional_int(code_id, "Código")
    except ValueError as exc:
        return _redirect_with_feedback(request, error=str(exc))

    classification_clean = _clean_text(classification)
    description_clean = _clean_text(description)

    if code_id_value:
        existing = waste_code_crud.get(db, code_id_value)
        if existing is None:
            return _redirect_with_feedback(request, error="Código de resíduo não encontrado.")
        try:
            payload_update = WasteCodeUpdate(
                code=code_clean,
                classification=classification_clean,
                description=description_clean,
            )
        except ValidationError as exc:
            return _redirect_with_feedback(request, error=_format_validation_errors(exc))
        try:
            waste_code_crud.update(db, existing, payload_update)
        except IntegrityError:
            db.rollback()
            return _redirect_with_feedback(request, error="Código de resíduo já cadastrado.")
        return _redirect_with_feedback(request, message="Código de resíduo atualizado com sucesso.")

    try:
        payload = WasteCodeCreate(
            code=code_clean,
            classification=classification_clean,
            description=description_clean,
        )
    except ValidationError as exc:
        return _redirect_with_feedback(request, error=_format_validation_errors(exc))

    try:
        waste_code_crud.create(db, payload)
    except IntegrityError:
        db.rollback()
        return _redirect_with_feedback(request, error="Código de resíduo já cadastrado.")

    return _redirect_with_feedback(request, message="Código de resíduo criado com sucesso.")


@router.post("/ui/residues/transporters", response_class=HTMLResponse)
async def create_transporter_form(
    request: Request,
    transporter_id: str | None = Form(None),
    name: str = Form(...),
    license_number: str = Form(...),
    license_issue_date: str | None = Form(None),
    license_expiry_date: str | None = Form(None),
    contact_email: str | None = Form(None),
    contact_phone: str | None = Form(None),
    db: Session = Depends(deps.get_db),
) -> RedirectResponse:
    name_clean = _clean_text(name)
    license_number_clean = _clean_text(license_number)
    if not name_clean or not license_number_clean:
        return _redirect_with_feedback(request, error="Nome e licença são obrigatórios.")

    try:
        issue_date_value = _parse_optional_date(license_issue_date, "Data de emissão")
        expiry_date_value = _parse_optional_date(license_expiry_date, "Data de validade")
    except ValueError as exc:
        return _redirect_with_feedback(request, error=str(exc))

    try:
        transporter_id_value = _parse_optional_int(transporter_id, "Transportadora")
    except ValueError as exc:
        return _redirect_with_feedback(request, error=str(exc))

    contact_email_clean = _clean_text(contact_email)
    contact_phone_clean = _clean_text(contact_phone)

    if transporter_id_value:
        existing = transporter_crud.get(db, transporter_id_value)
        if existing is None:
            return _redirect_with_feedback(request, error="Transportadora não encontrada.")
        try:
            payload_update = TransporterUpdate(
                name=name_clean,
                license_number=license_number_clean,
                license_issue_date=issue_date_value,
                license_expiry_date=expiry_date_value,
                contact_email=contact_email_clean,
                contact_phone=contact_phone_clean,
            )
        except ValidationError as exc:
            return _redirect_with_feedback(request, error=_format_validation_errors(exc))
        try:
            transporter_crud.update(db, existing, payload_update)
        except IntegrityError:
            db.rollback()
            return _redirect_with_feedback(request, error="Já existe uma transportadora com esses dados.")
        return _redirect_with_feedback(request, message="Transportadora atualizada com sucesso.")

    try:
        payload = TransporterCreate(
            name=name_clean,
            license_number=license_number_clean,
            license_issue_date=issue_date_value,
            license_expiry_date=expiry_date_value,
            contact_email=contact_email_clean,
            contact_phone=contact_phone_clean,
        )
    except ValidationError as exc:
        return _redirect_with_feedback(request, error=_format_validation_errors(exc))

    try:
        transporter_crud.create(db, payload)
    except IntegrityError:
        db.rollback()
        return _redirect_with_feedback(request, error="Já existe uma transportadora com esses dados.")

    return _redirect_with_feedback(request, message="Transportadora cadastrada com sucesso.")


@router.post("/ui/residues/recipients", response_class=HTMLResponse)
async def create_recipient_form(
    request: Request,
    recipient_id: str | None = Form(None),
    name: str = Form(...),
    facility_type: str | None = Form(None),
    license_number: str = Form(...),
    license_issue_date: str | None = Form(None),
    license_expiry_date: str | None = Form(None),
    contact_email: str | None = Form(None),
    contact_phone: str | None = Form(None),
    db: Session = Depends(deps.get_db),
) -> RedirectResponse:
    name_clean = _clean_text(name)
    license_number_clean = _clean_text(license_number)
    if not name_clean or not license_number_clean:
        return _redirect_with_feedback(request, error="Nome e licença são obrigatórios.")

    try:
        issue_date_value = _parse_optional_date(license_issue_date, "Data de emissão")
        expiry_date_value = _parse_optional_date(license_expiry_date, "Data de validade")
    except ValueError as exc:
        return _redirect_with_feedback(request, error=str(exc))

    try:
        recipient_id_value = _parse_optional_int(recipient_id, "Destinatário")
    except ValueError as exc:
        return _redirect_with_feedback(request, error=str(exc))

    facility_type_clean = _clean_text(facility_type)
    contact_email_clean = _clean_text(contact_email)
    contact_phone_clean = _clean_text(contact_phone)

    if recipient_id_value:
        existing = recipient_crud.get(db, recipient_id_value)
        if existing is None:
            return _redirect_with_feedback(request, error="Destinatário não encontrado.")
        try:
            payload_update = RecipientUpdate(
                name=name_clean,
                facility_type=facility_type_clean,
                license_number=license_number_clean,
                license_issue_date=issue_date_value,
                license_expiry_date=expiry_date_value,
                contact_email=contact_email_clean,
                contact_phone=contact_phone_clean,
            )
        except ValidationError as exc:
            return _redirect_with_feedback(request, error=_format_validation_errors(exc))
        try:
            recipient_crud.update(db, existing, payload_update)
        except IntegrityError:
            db.rollback()
            return _redirect_with_feedback(request, error="Já existe um destinatário com esses dados.")
        return _redirect_with_feedback(request, message="Destinatário atualizado com sucesso.")

    try:
        payload = RecipientCreate(
            name=name_clean,
            facility_type=facility_type_clean,
            license_number=license_number_clean,
            license_issue_date=issue_date_value,
            license_expiry_date=expiry_date_value,
            contact_email=contact_email_clean,
            contact_phone=contact_phone_clean,
        )
    except ValidationError as exc:
        return _redirect_with_feedback(request, error=_format_validation_errors(exc))

    try:
        recipient_crud.create(db, payload)
    except IntegrityError:
        db.rollback()
        return _redirect_with_feedback(request, error="Já existe um destinatário com esses dados.")

    return _redirect_with_feedback(request, message="Destinatário cadastrado com sucesso.")


@router.post("/ui/residues/waste-codes/{code_id}/delete", response_class=HTMLResponse)
async def delete_waste_code_form(request: Request, code_id: int, db: Session = Depends(deps.get_db)) -> RedirectResponse:
    try:
        waste_code_crud.remove(db, code_id)
    except ValueError:
        return _redirect_with_feedback(request, error="Código de resíduo não encontrado.")
    return _redirect_with_feedback(request, message="Código de resíduo removido com sucesso.")


@router.post("/ui/residues/transporters/{transporter_id}/delete", response_class=HTMLResponse)
async def delete_transporter_form(
    request: Request,
    transporter_id: int,
    db: Session = Depends(deps.get_db),
) -> RedirectResponse:
    try:
        transporter_crud.remove(db, transporter_id)
    except ValueError:
        return _redirect_with_feedback(request, error="Transportadora não encontrada.")
    return _redirect_with_feedback(request, message="Transportadora removida com sucesso.")


@router.post("/ui/residues/recipients/{recipient_id}/delete", response_class=HTMLResponse)
async def delete_recipient_form(
    request: Request,
    recipient_id: int,
    db: Session = Depends(deps.get_db),
) -> RedirectResponse:
    try:
        recipient_crud.remove(db, recipient_id)
    except ValueError:
        return _redirect_with_feedback(request, error="Destinatário não encontrado.")
    return _redirect_with_feedback(request, message="Destinatário removido com sucesso.")
