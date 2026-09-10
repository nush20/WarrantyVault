import calendar
import math
from datetime import date, timedelta

from sqlalchemy import Select, delete, func, select
from sqlalchemy.orm import Session

from backend.models.notification import Notification
from backend.models.product import Product
from backend.schemas.product import ProductCreate, ProductPage, ProductUpdate
from backend.services.reminder_preference_service import DEFAULT_REMINDER_DAYS, set_preferences
from backend.utils.exceptions import AppError, NotFoundError


def add_months(value: date, months: int) -> date:
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def _expiry(purchase_date: date | None, warranty_months: int | None) -> date | None:
    if purchase_date is None or warranty_months is None:
        return None
    return add_months(purchase_date, warranty_months)


def create_product(db: Session, owner_id: str, data: ProductCreate) -> Product:
    values = data.model_dump()
    values["warranty_expiry_date"] = data.warranty_expiry_date or _expiry(
        data.purchase_date, data.warranty_months
    )
    product = Product(
        owner_id=owner_id,
        **values,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    set_preferences(db, owner_id, product.id, DEFAULT_REMINDER_DAYS)
    return product


def get_product(db: Session, owner_id: str, product_id: str) -> Product:
    product = db.scalar(select(Product).where(Product.id == product_id, Product.owner_id == owner_id))
    if not product:
        raise NotFoundError("Product not found")
    return product


def list_products(
    db: Session,
    owner_id: str,
    page: int,
    page_size: int,
    brand: str | None = None,
    category: str | None = None,
    warranty_status: str | None = None,
    purchased_from: date | None = None,
    purchased_to: date | None = None,
) -> ProductPage:
    query: Select = select(Product).where(Product.owner_id == owner_id)
    today = date.today()
    if brand:
        query = query.where(func.lower(Product.brand) == brand.lower())
    if category:
        query = query.where(func.lower(Product.category) == category.lower())
    if warranty_status == "active":
        query = query.where(Product.warranty_expiry_date >= today)
    elif warranty_status == "expired":
        query = query.where(Product.warranty_expiry_date < today)
    if purchased_from:
        query = query.where(Product.purchase_date >= purchased_from)
    if purchased_to:
        query = query.where(Product.purchase_date <= purchased_to)

    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    items = list(
        db.scalars(query.order_by(Product.created_at.desc()).offset((page - 1) * page_size).limit(page_size))
    )
    return ProductPage(
        items=items, total=total, page=page, page_size=page_size, pages=math.ceil(total / page_size)
    )


def update_product(db: Session, product: Product, data: ProductUpdate) -> Product:
    previous_expiry = product.warranty_expiry_date
    changes = data.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(product, field, value)
    if product.warranty_months is not None and product.purchase_date is None:
        raise AppError("purchase_date is required when warranty_months is provided")
    if "warranty_expiry_date" not in changes and {"purchase_date", "warranty_months"} & changes.keys():
        product.warranty_expiry_date = _expiry(product.purchase_date, product.warranty_months)
    if product.warranty_expiry_date != previous_expiry:
        db.execute(delete(Notification).where(Notification.product_id == product.id))
    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product: Product) -> None:
    db.delete(product)
    db.commit()


def expiring_products(db: Session, owner_id: str, days: int) -> list[Product]:
    today = date.today()
    return list(
        db.scalars(
            select(Product)
            .where(
                Product.owner_id == owner_id,
                Product.warranty_expiry_date >= today,
                Product.warranty_expiry_date <= today + timedelta(days=days),
            )
            .order_by(Product.warranty_expiry_date)
        )
    )
