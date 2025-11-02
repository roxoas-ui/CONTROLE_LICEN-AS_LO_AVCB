from pathlib import Path
from typing import Literal
from uuid import uuid4

from fastapi import UploadFile

from app.config import get_settings

StorageCategory = Literal["licenses", "transporters", "recipients", "avcb"]


def save_upload(file: UploadFile, category: StorageCategory) -> str:
    settings = get_settings()
    storage_dir = Path(settings.file_storage_dir) / category
    storage_dir.mkdir(parents=True, exist_ok=True)
    file_extension = Path(file.filename or "").suffix or ".pdf"
    filename = f"{uuid4().hex}{file_extension}"
    destination = storage_dir / filename
    with destination.open("wb") as buffer:
        buffer.write(file.file.read())
    return str(destination)
