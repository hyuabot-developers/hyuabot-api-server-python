__version__ = "1.0.0-alpha1"

import functools

import aioredis
from aioredis import Redis
from fastapi import FastAPI

from app.hyuabot.api.initialize_data import initialize_data
from app.hyuabot.api.api.api_v1 import API_V1_ROUTERS
from app.hyuabot.api.core.config import AppSettings


def create_app(app_settings: AppSettings) -> FastAPI:
    app = FastAPI()
    app.add_event_handler("startup", functools.partial(_web_app_startup, app, app_settings))
    app.add_event_handler("shutdown", functools.partial(_web_app_shutdown, app))

    for router in API_V1_ROUTERS:
        app.include_router(router, prefix=app_settings.API_V1_STR)
    return app


async def _web_app_startup(app: FastAPI, app_settings: AppSettings) -> None:
    redis_connection_pool = aioredis.from_url(app_settings.REDIS_URI)
    await initialize_data(redis_connection_pool)
    app.extra["redis_connection_pool"] = redis_connection_pool


async def _web_app_shutdown(app: FastAPI) -> None:
    redis_connection_pool: Redis = app.extra["redis_connection_pool"]
    await redis_connection_pool.close()
