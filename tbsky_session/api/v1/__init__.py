from fastapi import APIRouter

from .security import security_router

routers: list[APIRouter] = [security_router]
