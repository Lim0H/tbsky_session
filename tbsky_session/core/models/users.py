from typing import Annotated

from pydantic import EmailStr
from pydantic import Field as PydanticField
from pydantic.experimental.pipeline import validate_as
from sqlmodel import Field

from ..schema import BaseSchema
from ..security import PasswordTools
from .base_model import BaseModel, PrimaryKeyType, make_primary_key

__all__ = ["User", "UserBase"]


class UserBase(BaseSchema):
    first_name: str = PydanticField(min_length=3)
    last_name: str = PydanticField(min_length=3)

    email: EmailStr


class User(BaseModel, UserBase, table=True):
    __tablename__ = "users"

    user_id: PrimaryKeyType = make_primary_key()

    email: EmailStr = Field()
    hashed_password: Annotated[
        str, validate_as(str).transform(PasswordTools.get_password_hash)
    ] = Field()
