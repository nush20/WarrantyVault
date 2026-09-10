from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ProductFields(BaseModel):
    product_name: str = Field(min_length=1, max_length=200)
    category: str | None = Field(default=None, max_length=100)
    brand: str | None = Field(default=None, max_length=100)
    seller: str | None = Field(default=None, max_length=200)
    purchase_date: date | None = None
    price: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    serial_number: str | None = Field(default=None, max_length=200)
    invoice_number: str | None = Field(default=None, max_length=200)
    warranty_months: int | None = Field(default=None, ge=0, le=1200)
    warranty_expiry_date: date | None = None
    warranty_provider: str | None = Field(default=None, max_length=200)
    support_url: str | None = Field(default=None, max_length=500)
    support_phone: str | None = Field(default=None, max_length=100)
    support_email: str | None = Field(default=None, max_length=320)
    notes: str | None = None

    @model_validator(mode="after")
    def warranty_needs_purchase_date(self):
        if self.warranty_months is not None and self.purchase_date is None:
            raise ValueError("purchase_date is required when warranty_months is provided")
        return self


class ProductCreate(ProductFields):
    pass


class ProductUpdate(BaseModel):
    product_name: str | None = Field(default=None, min_length=1, max_length=200)
    category: str | None = Field(default=None, max_length=100)
    brand: str | None = Field(default=None, max_length=100)
    seller: str | None = Field(default=None, max_length=200)
    purchase_date: date | None = None
    price: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    serial_number: str | None = Field(default=None, max_length=200)
    invoice_number: str | None = Field(default=None, max_length=200)
    warranty_months: int | None = Field(default=None, ge=0, le=1200)
    warranty_expiry_date: date | None = None
    warranty_provider: str | None = Field(default=None, max_length=200)
    support_url: str | None = Field(default=None, max_length=500)
    support_phone: str | None = Field(default=None, max_length=100)
    support_email: str | None = Field(default=None, max_length=320)
    notes: str | None = None


class ProductResponse(ProductFields):
    id: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ProductPage(BaseModel):
    items: list[ProductResponse]
    total: int
    page: int
    page_size: int
    pages: int


class ReminderPreferences(BaseModel):
    days_before: list[int] = Field(default=[30, 7])

    @model_validator(mode="after")
    def validate_days(self):
        allowed = {1, 7, 30}
        if len(self.days_before) != len(set(self.days_before)):
            raise ValueError("Reminder days must be unique")
        if not set(self.days_before).issubset(allowed):
            raise ValueError("Reminder days must contain only 1, 7, or 30")
        return self
