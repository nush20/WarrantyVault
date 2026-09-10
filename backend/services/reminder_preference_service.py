from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from backend.models.notification import Notification
from backend.models.reminder_preference import ReminderPreference

DEFAULT_REMINDER_DAYS = [30, 7]


def get_preferences(db: Session, owner_id: str, product_id: str) -> list[int]:
    return list(
        db.scalars(
            select(ReminderPreference.days_before)
            .where(
                ReminderPreference.owner_id == owner_id,
                ReminderPreference.product_id == product_id,
            )
            .order_by(ReminderPreference.days_before.desc())
        )
    )


def set_preferences(db: Session, owner_id: str, product_id: str, days: list[int]) -> list[int]:
    db.execute(
        delete(ReminderPreference).where(
            ReminderPreference.owner_id == owner_id,
            ReminderPreference.product_id == product_id,
        )
    )
    db.execute(
        delete(Notification).where(
            Notification.owner_id == owner_id,
            Notification.product_id == product_id,
            Notification.status.in_(["pending", "failed"]),
        )
    )
    db.add_all(
        ReminderPreference(owner_id=owner_id, product_id=product_id, days_before=day)
        for day in sorted(set(days), reverse=True)
    )
    db.commit()
    return get_preferences(db, owner_id, product_id)
