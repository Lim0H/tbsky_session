from typing import Optional

from fastapi import Cookie, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from ..models import User
from ..repository import BlackListTokenRepository, UserRepository
from ..security import decode_jwt_token

__all__ = ["PublicResource", "ProtectedResource", "get_user_by_access_token"]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


async def get_user_by_access_token(
    access_token_from_header: Optional[str] = Depends(oauth2_scheme),
    access_token: Optional[str] = Cookie(None),
    refresh_token: Optional[str] = Cookie(None),
    user_repository: UserRepository = Depends(),
    black_list_token_repository: BlackListTokenRepository = Depends(),
) -> User:
    if access_token := (access_token_from_header or access_token):
        access_token_payload = decode_jwt_token(access_token)
        user_id: str = access_token_payload.get("sub")  # type: ignore

        if await black_list_token_repository.get(access_token):
            raise HTTPException(status_code=401, detail="Invalid access token")
        if refresh_token and await black_list_token_repository.get(refresh_token):
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        if user := (await user_repository.get_first(user_id=user_id)):
            return user
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    raise HTTPException(status_code=401, detail="Invalid access token")


class PublicResource:
    pass


class ProtectedResource(PublicResource):
    user: User = Depends(get_user_by_access_token)
