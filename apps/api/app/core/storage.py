import uuid
from pathlib import Path

from app.core.config import settings

ALLOWED_SUFFIXES = {".pdf", ".png", ".jpg", ".jpeg", ".webp", ".html", ".txt"}


def save_upload(data: bytes, filename: str) -> str:
    """Persist an upload on local disk and return its relative path."""
    directory = Path(settings.storage_dir)
    directory.mkdir(parents=True, exist_ok=True)
    suffix = Path(filename or "upload.bin").suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise ValueError("不支持的文件扩展名")
    target = directory / f"{uuid.uuid4().hex}{suffix}"
    target.write_bytes(data)
    return str(target)


def save_snapshot(data: bytes, suffix: str = ".html") -> str:
    """Persist a fetched page snapshot (URL imports) on local disk."""
    directory = Path(settings.storage_dir)
    directory.mkdir(parents=True, exist_ok=True)
    suffix = suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        suffix = ".txt"
    target = directory / f"{uuid.uuid4().hex}{suffix}"
    target.write_bytes(data)
    return str(target)
