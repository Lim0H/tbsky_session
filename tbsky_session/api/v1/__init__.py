from fastapi import APIRouter

from .security import security_router, users_router

routers: list[APIRouter] = [security_router, users_router]
