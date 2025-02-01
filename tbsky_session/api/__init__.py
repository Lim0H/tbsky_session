import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
import uvicorn.server
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from tbsky_session.core import AppSettings, get_redis_connection, initialize_database

from .v1 import routers

__all__ = ["init_fastapi_server"]

log = logging.getLogger(__file__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    redis = get_redis_connection()
    log.info(f"Connected to redis: {await redis.ping()}")
    FastAPICache.init(RedisBackend(redis), prefix="tbsky-session")
    await initialize_database()
    yield


def init_fastapi_server() -> FastAPI:
    app = FastAPI(
        title="TBSky Session Service",
        lifespan=lifespan,
        docs_url="/session/docs",  # Customizing Swagger UI path
        openapi_url="/session/docs/openapi.json",  # Customizing OpenAPI JSON path
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

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
