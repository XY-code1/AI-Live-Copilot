import uuid
from pathlib import Path

from app.core.config import settings


def save_upload(data: bytes, filename: str) -> str:
    """Persist an upload on local disk and return its relative path."""
    directory = Path(settings.storage_dir)
    directory.mkdir(parents=True, exist_ok=True)
    suffix = Path(filename or "upload.pdf").suffix or ".pdf"
    target = directory / f"{uuid.uuid4().hex}{suffix}"
    target.write_bytes(data)
    return str(target)
