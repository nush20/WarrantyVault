from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.session import Base
from backend.models.base import UUIDTimestampMixin


class ReminderPreference(UUIDTimestampMixin, Base):
    __tablename__ = "reminder_preferences"
    __table_args__ = (UniqueConstraint("product_id", "days_before", name="uq_product_reminder_preference"),)

    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    days_before: Mapped[int] = mapped_column(Integer)
