from app.crud.avcb import avcb_crud
from app.crud.license import license_crud
from app.crud.residue import (
	recipient_crud,
	storage_code_crud,
	transporter_crud,
	waste_code_crud,
)
from app.crud.user import user_crud

__all__ = [
	"user_crud",
	"license_crud",
	"avcb_crud",
	"waste_code_crud",
	"storage_code_crud",
	"transporter_crud",
	"recipient_crud",
]
