from datetime import date
from typing import Literal

from fastapi import APIRouter, Query, Response, status

from backend.schemas.product import (
    ProductCreate,
    ProductPage,
    ProductResponse,
    ProductUpdate,
    ReminderPreferences,
)
from backend.services import product_service
from backend.services.reminder_preference_service import get_preferences, set_preferences
from backend.utils.dependencies import CurrentUser, DbSession

router = APIRouter(prefix="/products", tags=["products"])


@router.post("", response_model=ProductResponse, status_code=201)
def create_product(data: ProductCreate, db: DbSession, user: CurrentUser):
    return product_service.create_product(db, user.id, data)


@router.get("", response_model=ProductPage)
def list_products(
    db: DbSession,
    user: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    brand: str | None = None,
    category: str | None = None,
    warranty_status: Literal["active", "expired"] | None = None,
    purchased_from: date | None = None,
    purchased_to: date | None = None,
):
    return product_service.list_products(
        db, user.id, page, page_size, brand, category, warranty_status, purchased_from, purchased_to
    )


@router.get("/expiring", response_model=list[ProductResponse])
def expiring(db: DbSession, user: CurrentUser, days: int = Query(30, ge=0, le=3650)):
    return product_service.expiring_products(db, user.id, days)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: str, db: DbSession, user: CurrentUser):
    return product_service.get_product(db, user.id, product_id)


@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(product_id: str, data: ProductUpdate, db: DbSession, user: CurrentUser):
    product = product_service.get_product(db, user.id, product_id)
    return product_service.update_product(db, product, data)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: str, db: DbSession, user: CurrentUser):
    product_service.delete_product(db, product_service.get_product(db, user.id, product_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{product_id}/reminders", response_model=ReminderPreferences)
def product_reminders(product_id: str, db: DbSession, user: CurrentUser):
    product_service.get_product(db, user.id, product_id)
    return ReminderPreferences(days_before=get_preferences(db, user.id, product_id))


@router.put("/{product_id}/reminders", response_model=ReminderPreferences)
def update_product_reminders(
    product_id: str,
    data: ReminderPreferences,
    db: DbSession,
    user: CurrentUser,
):
    product_service.get_product(db, user.id, product_id)
    return ReminderPreferences(days_before=set_preferences(db, user.id, product_id, data.days_before))
