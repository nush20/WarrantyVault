from pathlib import Path

import requests

from backend.config import get_settings
from backend.models.document import Document
from backend.utils.exceptions import ServiceUnavailableError


def _object_path(document: Document) -> str:
    return f"{document.owner_id}/{document.stored_filename}"


def _supabase_headers(content_type: str | None = None) -> dict[str, str]:
    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_service_key:
        raise ServiceUnavailableError("Supabase Storage is not configured")
    headers = {
        "Authorization": f"Bearer {settings.supabase_service_key}",
        "apikey": settings.supabase_service_key,
    }
    if content_type:
        headers["Content-Type"] = content_type
    return headers


def _supabase_object_url(document: Document, authenticated: bool = False) -> str:
    settings = get_settings()
    prefix = "object/authenticated" if authenticated else "object"
    base_url = (settings.supabase_url or "").rstrip("/")
    return f"{base_url}/storage/v1/{prefix}/{settings.supabase_bucket}/{_object_path(document)}"


def save(document: Document, content: bytes) -> None:
    settings = get_settings()
    if settings.storage_backend == "local":
        path = local_path(document)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return
    if settings.storage_backend != "supabase":
        raise ServiceUnavailableError("Unknown document storage backend")
    try:
        response = requests.post(
            _supabase_object_url(document),
            headers={**_supabase_headers(document.content_type), "x-upsert": "false"},
            data=content,
            timeout=30,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise ServiceUnavailableError("Document storage is temporarily unavailable") from exc


def read(document: Document) -> bytes:
    settings = get_settings()
    if settings.storage_backend == "local":
        try:
            return local_path(document).read_bytes()
        except OSError as exc:
            raise ServiceUnavailableError("The stored document could not be read") from exc
    try:
        response = requests.get(
            _supabase_object_url(document, authenticated=True),
            headers=_supabase_headers(),
            timeout=30,
        )
        response.raise_for_status()
        return response.content
    except requests.RequestException as exc:
        raise ServiceUnavailableError("The stored document could not be read") from exc


def remove(document: Document) -> None:
    settings = get_settings()
    if settings.storage_backend == "local":
        local_path(document).unlink(missing_ok=True)
        return
    try:
        response = requests.delete(
            _supabase_object_url(document),
            headers=_supabase_headers(),
            timeout=30,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise ServiceUnavailableError("The stored document could not be deleted") from exc


def local_path(document: Document) -> Path:
    return get_settings().upload_dir / document.owner_id / document.stored_filename
