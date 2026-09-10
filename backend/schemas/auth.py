from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    reminder_email_enabled: bool
    model_config = ConfigDict(from_attributes=True)


class UserReminderSettings(BaseModel):
    email: EmailStr
    reminder_email_enabled: bool


class UserReminderSettingsUpdate(BaseModel):
    reminder_email_enabled: bool


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
