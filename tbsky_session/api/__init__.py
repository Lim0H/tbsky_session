import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
import uvicorn.server
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from tbsky_session.core import get_redis_connection
from tbsky_session.core.config import AppSettings

from .v1 import routers

__all__ = ["init_fastapi_server"]

log = logging.getLogger(__file__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    redis = get_redis_connection()
    log.info(f"Connected to redis: {await redis.ping()}")
    FastAPICache.init(RedisBackend(redis), prefix="tbsky-session")
    yield


def init_fastapi_server() -> FastAPI:
    app = FastAPI(title="TBSky Session Service", lifespan=lifespan)

    for router in routers:
        app.include_router(router, prefix="/api/v1")

    return app


async def run_fastapi_server():
    app = init_fastapi_server()

    config = uvicorn.Config(
        app, host=str(AppSettings.server.HOST), port=AppSettings.server.PORT
    )
    server = uvicorn.Server(config)
    await server.serve()
