from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.session import Base
from backend.models.base import UUIDTimestampMixin


class Product(UUIDTimestampMixin, Base):
    __tablename__ = "products"

    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    product_name: Mapped[str] = mapped_column(String(200), index=True)
    category: Mapped[str | None] = mapped_column(String(100), index=True)
    brand: Mapped[str | None] = mapped_column(String(100), index=True)
    seller: Mapped[str | None] = mapped_column(String(200))
    purchase_date: Mapped[date | None] = mapped_column(Date)
    price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    serial_number: Mapped[str | None] = mapped_column(String(200))
    invoice_number: Mapped[str | None] = mapped_column(String(200))
    warranty_months: Mapped[int | None] = mapped_column(Integer)
    warranty_expiry_date: Mapped[date | None] = mapped_column(Date, index=True)
    warranty_provider: Mapped[str | None] = mapped_column(String(200))
    support_url: Mapped[str | None] = mapped_column(String(500))
    support_phone: Mapped[str | None] = mapped_column(String(100))
    support_email: Mapped[str | None] = mapped_column(String(320))
    notes: Mapped[str | None] = mapped_column(Text)

    owner = relationship("User", back_populates="products")
    documents = relationship("Document", secondary="product_documents", back_populates="products")
