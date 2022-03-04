from typing import Any

import aioredis
from aioredis import Redis

from app.hyuabot.api.core.config import AppSettings


async def get_redis_connection(database_name: str) -> Redis:
    redis_connection: Redis = aioredis.from_url(f"{AppSettings().REDIS_URI}/{database_name}")
    return redis_connection


async def set_redis_value(redis_connection: Redis, key: str, value: Any) -> None:
    async with redis_connection.client() as redis_client:
        await redis_client.set(key, value)


async def get_redis_value(redis_connection: Redis, key: str) -> Any:
    async with redis_connection.client() as redis_client:
        value: Any = await redis_client.get(key)
        return value
