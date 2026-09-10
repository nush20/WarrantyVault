from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.models.product import Product
from backend.schemas.analytics import AnalyticsSummary


def summary(db: Session, owner_id: str, expiring_within_days: int) -> AnalyticsSummary:
    today = date.today()
    base = (Product.owner_id == owner_id,)
    total = db.scalar(select(func.count(Product.id)).where(*base)) or 0
    active = (
        db.scalar(select(func.count(Product.id)).where(*base, Product.warranty_expiry_date >= today)) or 0
    )
    expired = (
        db.scalar(select(func.count(Product.id)).where(*base, Product.warranty_expiry_date < today)) or 0
    )
    soon = (
        db.scalar(
            select(func.count(Product.id)).where(
                *base,
                Product.warranty_expiry_date >= today,
                Product.warranty_expiry_date <= today + timedelta(days=expiring_within_days),
            )
        )
        or 0
    )
    return AnalyticsSummary(
        total_products=total,
        active_warranties=active,
        expired_warranties=expired,
        expiring_soon=soon,
        expiring_within_days=expiring_within_days,
    )
