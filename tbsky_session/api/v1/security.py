from typing import Annotated

from fastapi import APIRouter, Body, Cookie, Depends, HTTPException, Response
from fastapi_restful.cbv import cbv

from tbsky_session.core import (
    BlackListToken,
    BlackListTokenRepository,
    PasswordTools,
    ProtectedResource,
    PublicResource,
    User,
    UserRepository,
    create_access_token,
    create_refresh_token,
    decode_jwt_token,
)
from tbsky_session.schemas import UserCreate, UserLogin
from tbsky_session.schemas.users import UserOut

__all__ = ["security_router", "users_router"]

users_router = APIRouter(prefix="/users", tags=["Users"])
security_router = APIRouter(prefix="/security", tags=["Auth"])


class SecurityResource:

    def _set_response_cookie(self, response: Response, user: User):
        access_token, expire_access_token_seconds = create_access_token(
            to_encode={"sub": str(user.user_id)}
        )
        refresh_token, expire_refresh_token_seconds = create_refresh_token(
            to_encode={"sub": str(user.user_id)}
        )
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            max_age=expire_access_token_seconds,
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            max_age=expire_refresh_token_seconds,
        )


@cbv(security_router)
class PublickAuthResource(PublicResource, SecurityResource):
    @security_router.post("/register")
    async def register(
        self,
        response: Response,
        user_create: UserCreate,
        user_repository: UserRepository = Depends(),
    ):
        async with user_repository.async_session_factory() as session:
            new_user = await user_repository.add(
                User.model_validate(
                    User(
                        first_name=user_create.first_name,
                        last_name=user_create.last_name,
                        email=user_create.email,
                        hashed_password=user_create.password.get_secret_value(),
                    )
                ),
                session=session,
            )
            self._set_response_cookie(response, new_user)

    @security_router.post("/login")
    async def login_from_user(
        self,
        response: Response,
        user: Annotated[UserLogin, Body()],
        user_repository: UserRepository = Depends(),
    ):
        if found_user := (await user_repository.get_first(email=user.email)):
            if PasswordTools.verify_password(
                user.password.get_secret_value(), found_user.hashed_password
            ):
                self._set_response_cookie(response, found_user)
                return
        raise HTTPException(status_code=401, detail="Incorrect username or password")


@cbv(security_router)
class AuthResource(ProtectedResource, SecurityResource):

    @security_router.post("/access_token")
    async def login_for_access_token(
        self,
        response: Response,
    ):
        self._set_response_cookie(response, self.user)
        return {"message": "Login successful"}

    @security_router.post("/refresh_token")
    async def refresh_access_token(
        self,
        response: Response,
        refresh_token: str = Cookie(),
    ):
        user_id_from_refresh = decode_jwt_token(refresh_token).get("sub")
        if str(self.user.user_id) != user_id_from_refresh:
            raise HTTPException(status_code=401, detail="Invalid access token")
        self._set_response_cookie(response, self.user)
        return {"message": "Login successful"}

    @security_router.post("/logout")
    async def logout(
        self,
        response: Response,
        black_list_token_repository: BlackListTokenRepository = Depends(),
        access_token: str = Cookie(),
        refresh_token: str = Cookie(),
    ):
        await black_list_token_repository.add(
            BlackListToken(access_token=access_token, refresh_token=refresh_token)
        )
        await black_list_token_repository.add(
            BlackListToken(access_token=refresh_token, refresh_token=refresh_token)
        )
        response.delete_cookie(key="access_token")
        response.delete_cookie(key="refresh_token")
        return {"message": "Logout successful"}


@cbv(users_router)
class UsersResource(ProtectedResource):
    @users_router.get("/me", response_model=UserOut)
    async def get_me(self, user_repository: UserRepository = Depends()):
        return self.user
