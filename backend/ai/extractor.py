from datetime import date
from decimal import Decimal
from io import BytesIO
from pathlib import Path

from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from pypdf import PdfReader

from backend.config import get_settings
from backend.utils.exceptions import AppError, ServiceUnavailableError


class ExtractedItem(BaseModel):
    product_name: str = Field(description="Purchased product name")
    brand: str | None = None
    price: Decimal | None = Field(default=None, ge=0)
    serial_number: str | None = None
    warranty_months: int | None = Field(default=None, ge=0)


class ExtractedInvoice(BaseModel):
    invoice_number: str | None = None
    purchase_date: date | None = Field(default=None, description="Purchase date")
    seller: str | None = None
    items: list[ExtractedItem] = Field(min_length=1)


def extract_pdf_text(source: Path | bytes) -> str:
    try:
        pdf_source = BytesIO(source) if isinstance(source, bytes) else source
        text = "\n\f\n".join(page.extract_text() or "" for page in PdfReader(pdf_source).pages).strip()
    except Exception as exc:
        raise AppError("The PDF could not be read") from exc
    if not text:
        raise AppError("No selectable text was found; scanned-image OCR is not enabled")
    return text


def extract_product_fields(text: str) -> ExtractedInvoice:
    settings = get_settings()
    if not settings.gemini_api_key:
        raise ServiceUnavailableError("GEMINI_API_KEY is required for AI extraction")
    llm = ChatGoogleGenerativeAI(
        model=settings.chat_model,
        google_api_key=settings.gemini_api_key,
        temperature=0,
    )
    structured_llm = llm.with_structured_output(ExtractedInvoice)
    try:
        return structured_llm.invoke(
            "Extract every purchased product from this receipt or invoice. Exclude taxes, delivery fees, "
            "discounts, totals, and other non-product line items. "
            "Extract warranty duration only when explicitly written on the invoice. "
            "Use null when a field is not stated; never invent values.\n\n" + text[:30000]
        )
    except Exception as exc:
        raise ServiceUnavailableError(
            "Gemini extraction failed. Check the API key, model access, and quota, then try again."
        ) from exc
