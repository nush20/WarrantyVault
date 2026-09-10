from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, computed_field


class NotificationResponse(BaseModel):
    id: str
    product_id: str
    title: str
    message: str
    warranty_expiry_date: date
    days_before: int
    scheduled_for: date
    status: str
    sent_at: datetime | None
    attempt_count: int
    is_read: bool
    created_at: datetime

    @computed_field
    @property
    def reminder_date(self) -> date:
        return self.scheduled_for

    model_config = ConfigDict(from_attributes=True)


class ReminderRunResponse(BaseModel):
    created: int
    sent: int
    failed: int
    checked_at: date
