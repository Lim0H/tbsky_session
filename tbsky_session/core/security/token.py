from datetime import UTC, datetime, timedelta
from typing import Any

import dateparser
import jwt
from fastapi import HTTPException

from ..config import AppSettings

REDIS_SECURITY_KEY = "security"

__all__ = ["create_access_token", "decode_jwt_token", "create_refresh_token"]


def create_jwt_token(data: dict) -> str:
    return jwt.encode(
        data,
        AppSettings.security.SECRET_KEY.get_secret_value(),
        algorithm=AppSettings.security.JWT_ALGORITHM,
    )


def decode_jwt_token(token: str) -> dict:
    try:
        payload: dict = jwt.decode(
            token,
            AppSettings.security.SECRET_KEY.get_secret_value(),
            algorithms=[AppSettings.security.JWT_ALGORITHM],
        )
        expire = dateparser.parse(payload.pop("expire"))
        if expire is None:
            raise jwt.InvalidTokenError
        if datetime.now(UTC).replace(tzinfo=None) > expire:
            raise jwt.ExpiredSignatureError
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401, detail="Token expired, please log in again"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def create_access_token(
    to_encode: dict[str, Any], expires_delta: timedelta | None = None
):
    if expires_delta:
        expire = datetime.now(UTC).replace(tzinfo=None) + expires_delta
    else:
        expire = datetime.now(UTC).replace(tzinfo=None) + timedelta(
            minutes=AppSettings.security.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"expire": str(expire)})
    return (
        create_jwt_token(to_encode),
        (expire - datetime.now(UTC).replace(tzinfo=None)).seconds,
    )


def create_refresh_token(
    to_encode: dict[str, Any], expires_delta: timedelta | None = None
):
    if expires_delta:
        expire = datetime.now(UTC).replace(tzinfo=None) + expires_delta
    else:
        expire = datetime.now(UTC).replace(tzinfo=None) + timedelta(
            days=AppSettings.security.REFRESH_TOKEN_EXPIRE_DAYS
        )
    to_encode.update({"expire": str(expire)})
    return (
        create_jwt_token(to_encode),
        (expire - datetime.now(UTC).replace(tzinfo=None)).seconds,
    )
