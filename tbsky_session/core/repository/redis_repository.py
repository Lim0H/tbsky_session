import logging
from abc import ABC
from typing import Callable, Optional, Type, TypeAlias, TypeVar

from redis.asyncio.client import Pipeline, Redis

from tbsky_session.core.db_session import get_redis_connection
from tbsky_session.core.models import BaseRedisModel
from tbsky_session.core.repository import GenericRepository
from tbsky_session.core.schema import BaseSchema

log = logging.getLogger(__file__)

__all__ = ["BaseRedisRepository"]


MODEL_VAR = TypeVar("MODEL_VAR", bound=BaseRedisModel)
EDIT_MODEL_VAR = TypeVar("EDIT_MODEL_VAR", bound=BaseSchema)

REDIS_CONNECTION: TypeAlias = Redis
PIPELINE_SESSION: TypeAlias = Pipeline


def pipeline_factory() -> PIPELINE_SESSION:
    connection = get_redis_connection()
    return connection.pipeline(transaction=True)


class BaseRedisRepository(GenericRepository[MODEL_VAR], ABC):
    model: Type[MODEL_VAR]

    redis_connection_factory: Callable[..., REDIS_CONNECTION] = (
        lambda _: get_redis_connection()
    )
    pipeline_factory: Callable[..., PIPELINE_SESSION] = lambda _: pipeline_factory()

    async def _callback_before_add(self, obj_new: MODEL_VAR) -> MODEL_VAR:
        return obj_new

    async def _add(
        self,
        obj_new: MODEL_VAR,
        db_session: PIPELINE_SESSION,
        with_execute=False,
    ) -> MODEL_VAR:
        """Commit new object to the database."""
        obj_new = await self._callback_before_add(obj_new)
        try:
            await db_session.set(obj_new.key, obj_new.model_dump_json())
            if with_execute:
                await db_session.execute()
            return obj_new
        except Exception:
            log.exception("Error while uploading new object to database")
            raise

    async def add(
        self,
        obj_new: MODEL_VAR,
        /,
        pipeline: Optional[PIPELINE_SESSION] = None,
        with_execute=True,
    ) -> MODEL_VAR:
        """Commit new object to the database."""
        obj_new = await self._callback_before_add(obj_new)
        if pipeline:
            return await self._add(obj_new, pipeline, with_execute)
        try:
            return await self._add(obj_new, self.pipeline_factory(), with_execute)
        except Exception:
            log.exception("Error while uploading new object to database")
            raise

    async def get(self, *keys: str) -> list[MODEL_VAR]:
        redis_connection = self.redis_connection_factory()
        values = await redis_connection.mget(*keys)
        return [self.model.model_validate_json(value) for value in values if value]
