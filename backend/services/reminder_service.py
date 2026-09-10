import asyncio
from contextlib import suppress
from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.config import get_settings
from backend.database.session import SessionLocal
from backend.models.notification import Notification
from backend.models.product import Product
from backend.models.reminder_preference import ReminderPreference
from backend.models.user import User
from backend.services.email_service import send_warranty_reminder
from backend.services.reminder_preference_service import DEFAULT_REMINDER_DAYS
from backend.utils.exceptions import NotFoundError


def _ensure_default_preferences(db: Session, owner_id: str | None = None) -> None:
    query = select(Product).where(
        ~select(ReminderPreference.id).where(ReminderPreference.product_id == Product.id).exists()
    )
    if owner_id:
        query = query.where(Product.owner_id == owner_id)
    for product in db.scalars(query):
        db.add_all(
            ReminderPreference(
                owner_id=product.owner_id,
                product_id=product.id,
                days_before=day,
            )
            for day in DEFAULT_REMINDER_DAYS
        )
    db.commit()


def create_reminders(db: Session, *, owner_id: str | None = None) -> dict[str, int]:
    today = date.today()
    _ensure_default_preferences(db, owner_id)
    query = (
        select(Product, ReminderPreference)
        .join(ReminderPreference, ReminderPreference.product_id == Product.id)
        .where(Product.warranty_expiry_date >= today)
    )
    if owner_id:
        query = query.where(Product.owner_id == owner_id)

    result = {"created": 0, "sent": 0, "failed": 0}
    for product, preference in db.execute(query):
        reminder_date = product.warranty_expiry_date - timedelta(days=preference.days_before)
        # Send only on the selected date; an outdated threshold is not useful to the user.
        if today != reminder_date:
            continue
        days_left = (product.warranty_expiry_date - today).days
        notification = db.scalar(
            select(Notification).where(
                Notification.owner_id == product.owner_id,
                Notification.product_id == product.id,
                Notification.warranty_expiry_date == product.warranty_expiry_date,
                Notification.days_before == preference.days_before,
            )
        )
        if not notification:
            notification = Notification(
                owner_id=product.owner_id,
                product_id=product.id,
                title=f"{product.product_name} warranty expires soon",
                message=(
                    f"Reminder scheduled for {reminder_date}. Your warranty expires on "
                    f"{product.warranty_expiry_date} ({days_left} days left)."
                ),
                warranty_expiry_date=product.warranty_expiry_date,
                days_before=preference.days_before,
                scheduled_for=reminder_date,
            )
            db.add(notification)
            try:
                db.commit()
                db.refresh(notification)
                result["created"] += 1
            except IntegrityError:
                db.rollback()
                notification = db.scalar(
                    select(Notification).where(
                        Notification.owner_id == product.owner_id,
                        Notification.product_id == product.id,
                        Notification.warranty_expiry_date == product.warranty_expiry_date,
                        Notification.days_before == preference.days_before,
                    )
                )
        if not notification or notification.status == "sent" or notification.attempt_count >= 3:
            continue

        user = db.scalar(select(User).where(User.id == product.owner_id))
        if not user.reminder_email_enabled:
            notification.status = "email_disabled"
            db.commit()
            continue
        notification.attempt_count += 1
        try:
            send_warranty_reminder(
                recipient=user.email,
                subject=notification.title,
                body=notification.message,
            )
            notification.status = "sent"
            notification.sent_at = datetime.now(UTC)
            result["sent"] += 1
        except Exception:
            notification.status = "failed"
            result["failed"] += 1
        finally:
            db.commit()
    return result


def list_notifications(db: Session, owner_id: str, unread_only: bool = False) -> list[Notification]:
    query = select(Notification).where(Notification.owner_id == owner_id)
    if unread_only:
        query = query.where(Notification.is_read.is_(False))
    return list(db.scalars(query.order_by(Notification.created_at.desc())))


def mark_read(db: Session, owner_id: str, notification_id: str) -> Notification:
    notification = db.scalar(
        select(Notification).where(Notification.id == notification_id, Notification.owner_id == owner_id)
    )
    if not notification:
        raise NotFoundError("Notification not found")
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return notification


def run_daily_reminders() -> None:
    with SessionLocal() as db:
        create_reminders(db)


async def reminder_worker() -> None:
    settings = get_settings()
    timezone = ZoneInfo(settings.reminder_timezone)
    while True:
        now = datetime.now(timezone)
        next_run = datetime.combine(now.date(), time(settings.reminder_hour), tzinfo=timezone)
        if next_run <= now:
            next_run += timedelta(days=1)
        await asyncio.sleep((next_run - now).total_seconds())
        await asyncio.to_thread(run_daily_reminders)


async def stop_reminder_worker(task: asyncio.Task) -> None:
    task.cancel()
    with suppress(asyncio.CancelledError):
        await task
