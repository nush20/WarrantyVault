from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from backend.schemas.auth import (
    Token,
    UserCreate,
    UserReminderSettings,
    UserReminderSettingsUpdate,
    UserResponse,
)
from backend.services import auth_service
from backend.utils.dependencies import CurrentUser, DbSession

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/signup", response_model=UserResponse, status_code=201)
def signup(data: UserCreate, db: DbSession):
    return auth_service.create_user(db, data)


@router.post("/login", response_model=Token)
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], db: DbSession):
    user = auth_service.authenticate(db, form.username, form.password)
    return Token(access_token=auth_service.create_access_token(user.id))


@router.get("/me/reminders", response_model=UserReminderSettings)
def reminder_settings(user: CurrentUser):
    return user


@router.patch("/me/reminders", response_model=UserReminderSettings)
def update_reminder_settings(data: UserReminderSettingsUpdate, db: DbSession, user: CurrentUser):
    user.reminder_email_enabled = data.reminder_email_enabled
    db.commit()
    db.refresh(user)
    return user
