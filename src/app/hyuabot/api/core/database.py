from aioredis import Redis
from fastapi.requests import Request


async def get_redis_connection(request: Request):
    redis_connection_pool: Redis = request.app.extra["redis_connection_pool"]
    return redis_connection_pool.client()
