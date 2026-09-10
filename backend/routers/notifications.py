from datetime import date

from fastapi import APIRouter

from backend.schemas.notification import NotificationResponse, ReminderRunResponse
from backend.services.reminder_service import create_reminders, list_notifications, mark_read
from backend.utils.dependencies import CurrentUser, DbSession

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationResponse])
def get_notifications(db: DbSession, user: CurrentUser, unread_only: bool = False):
    return list_notifications(db, user.id, unread_only)


@router.post("/generate", response_model=ReminderRunResponse)
def generate_reminders(
    db: DbSession,
    user: CurrentUser,
):
    result = create_reminders(db, owner_id=user.id)
    return ReminderRunResponse(**result, checked_at=date.today())


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
def read_notification(notification_id: str, db: DbSession, user: CurrentUser):
    return mark_read(db, user.id, notification_id)
