from typing import Annotated

from fastapi import APIRouter, File, Form, Response, UploadFile, status
from fastapi.responses import FileResponse

from backend.schemas.document import (
    DocumentResponse,
    ExtractionConfirmation,
    ExtractionResponse,
)
from backend.schemas.product import ProductResponse
from backend.services import document_service
from backend.utils.dependencies import CurrentUser, DbSession

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=list[DocumentResponse])
def product_documents(product_id: str, db: DbSession, user: CurrentUser):
    return document_service.list_documents(db, user.id, product_id)


@router.post("", response_model=DocumentResponse, status_code=201)
def upload_document(
    db: DbSession,
    user: CurrentUser,
    file: Annotated[UploadFile, File()],
    product_id: Annotated[str | None, Form()] = None,
):
    return document_service.save_upload(db, user.id, file, product_id)


@router.post("/{document_id}/extract", response_model=ExtractionResponse)
def extract_receipt(document_id: str, db: DbSession, user: CurrentUser):
    document = document_service.get_document(db, user.id, document_id)
    extracted = document_service.extract_product_preview(db, document)
    return ExtractionResponse(document=document, **extracted.model_dump())


@router.post("/{document_id}/confirm", response_model=list[ProductResponse], status_code=201)
def confirm_receipt(
    document_id: str,
    data: ExtractionConfirmation,
    db: DbSession,
    user: CurrentUser,
):
    document = document_service.get_document(db, user.id, document_id)
    return document_service.confirm_extracted_products(
        db,
        user.id,
        document,
        data.products,
        data.reminder_days,
    )


@router.get("/{document_id}/download", response_class=FileResponse)
def download_document(document_id: str, db: DbSession, user: CurrentUser):
    document = document_service.get_document(db, user.id, document_id)
    return FileResponse(
        document_service.stored_path(document),
        media_type=document.content_type,
        filename=document.original_filename,
    )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: str, db: DbSession, user: CurrentUser):
    document = document_service.get_document(db, user.id, document_id)
    document_service.delete_document(db, document)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
