from functools import cache

from redis import asyncio as aioredis
from redis.asyncio.client import Redis
from tbsky_session.core import AppSettings

__all__ = ["get_redis_connection"]


@cache
def get_redis_connection() -> Redis:
    return aioredis.from_url(str(AppSettings.database.REDIS_DSN))
