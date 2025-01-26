from pydantic import EmailStr, SecretStr, field_validator

from tbsky_session.core import BaseSchema, PasswordTools, PrimaryKeyType, UserBase

__all__ = ["UserCreate", "UserUpdate", "UserOut", "UserLogin"]


class UserCreate(UserBase):
    password: SecretStr

    @field_validator("password", mode="before")
    @classmethod
    def validate_password(cls, v: str):
        return PasswordTools.validate_password(v)


class UserLogin(BaseSchema):
    email: EmailStr
    password: SecretStr


class UserUpdate(UserBase):
    user_id: PrimaryKeyType
    password: SecretStr

    @field_validator("password", mode="before")
    @classmethod
    def validate_password(cls, v: str):
        return PasswordTools.validate_password(v)


class UserOut(UserBase):
    user_id: PrimaryKeyType
