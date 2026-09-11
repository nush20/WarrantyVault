from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from backend.ai.extractor import extract_pdf_text, extract_product_fields
from backend.config import get_settings
from backend.models.document import Document
from backend.models.product_document import ProductDocument
from backend.schemas.product import ProductCreate
from backend.services.product_service import create_product, get_product
from backend.services.reminder_preference_service import set_preferences
from backend.services import storage_service
from backend.utils.exceptions import AppError, NotFoundError

ALLOWED_CONTENT_TYPES = {"application/pdf", "image/jpeg", "image/png"}


def save_upload(db: Session, owner_id: str, upload: UploadFile, product_id: str | None) -> Document:
    settings = get_settings()
    if upload.content_type not in ALLOWED_CONTENT_TYPES:
        raise AppError("Only PDF, JPEG, and PNG files are supported")
    if product_id:
        get_product(db, owner_id, product_id)
    suffix = Path(upload.filename or "document").suffix.lower()
    stored_filename = f"{uuid4()}{suffix}"
    content = upload.file.read(settings.max_upload_mb * 1024 * 1024 + 1)
    if len(content) > settings.max_upload_mb * 1024 * 1024:
        raise AppError(f"File exceeds the {settings.max_upload_mb} MB limit")
    document = Document(
        owner_id=owner_id,
        original_filename=Path(upload.filename or "document").name,
        stored_filename=stored_filename,
        content_type=upload.content_type,
        size_bytes=len(content),
    )
    storage_service.save(document, content)
    db.add(document)
    try:
        db.commit()
    except Exception:
        db.rollback()
        storage_service.remove(document)
        raise
    db.refresh(document)
    if product_id:
        db.add(ProductDocument(product_id=product_id, document_id=document.id))
        db.commit()
    return document


def get_document(db: Session, owner_id: str, document_id: str) -> Document:
    document = db.scalar(select(Document).where(Document.id == document_id, Document.owner_id == owner_id))
    if not document:
        raise NotFoundError("Document not found")
    return document


def list_documents(db: Session, owner_id: str, product_id: str) -> list[Document]:
    get_product(db, owner_id, product_id)
    return list(
        db.scalars(
            select(Document)
            .join(ProductDocument, ProductDocument.document_id == Document.id)
            .where(Document.owner_id == owner_id, ProductDocument.product_id == product_id)
            .order_by(Document.created_at.desc())
        )
    )


def stored_path(document: Document) -> Path:
    return storage_service.local_path(document)


def stored_content(document: Document) -> bytes:
    return storage_service.read(document)


def delete_document(db: Session, document: Document) -> None:
    storage_service.remove(document)
    db.execute(delete(ProductDocument).where(ProductDocument.document_id == document.id))
    db.delete(document)
    db.commit()


def _text(document: Document) -> str:
    if document.content_type != "application/pdf":
        raise AppError(
            "Text extraction currently supports text-based PDFs; image OCR is optional and not enabled"
        )
    return extract_pdf_text(stored_content(document))


def extract_product_preview(db: Session, document: Document):
    text = document.extracted_text or _text(document)
    extracted = extract_product_fields(text)
    document.extracted_text = text
    db.commit()
    db.refresh(document)
    return extracted


def confirm_extracted_products(
    db: Session,
    owner_id: str,
    document: Document,
    product_data: list[ProductCreate],
    reminder_days: list[int],
):
    if db.scalar(select(ProductDocument.document_id).where(ProductDocument.document_id == document.id)):
        raise AppError("This document has already been confirmed")
    products = []
    for item in product_data:
        product = create_product(db, owner_id, item)
        set_preferences(db, owner_id, product.id, reminder_days)
        db.add(ProductDocument(product_id=product.id, document_id=document.id))
        products.append(product)
    db.commit()
    return products
