from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.schemas.product import ProductCreate


class DocumentResponse(BaseModel):
    id: str
    original_filename: str
    content_type: str
    size_bytes: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ExtractedItemPreview(BaseModel):
    product_name: str
    brand: str | None = None
    price: Decimal | None = None
    serial_number: str | None = None
    warranty_months: int | None = None


class ExtractionResponse(BaseModel):
    document: DocumentResponse
    invoice_number: str | None = None
    purchase_date: date | None = None
    seller: str | None = None
    items: list[ExtractedItemPreview]
    requires_confirmation: bool = True


class ExtractionConfirmation(BaseModel):
    products: list[ProductCreate] = Field(min_length=1)
    reminder_days: list[int] = Field(default=[30, 7])

    @field_validator("reminder_days")
    @classmethod
    def validate_reminder_days(cls, days: list[int]) -> list[int]:
        if len(days) != len(set(days)) or not set(days).issubset({1, 7, 30}):
            raise ValueError("Reminder days must be unique and contain only 1, 7, or 30")
        return days
