__version__ = "1.0.0-alpha1"

import functools

from aioredis import Redis
from fastapi import FastAPI

from app.hyuabot.api.api.api_v1 import API_V1_ROUTERS
from app.hyuabot.api.core.config import AppSettings
from app.hyuabot.api.initialize_data import initialize_data


def create_app(app_settings: AppSettings) -> FastAPI:
    app = FastAPI()
    app.add_event_handler("startup", _web_app_startup)

    for router in API_V1_ROUTERS:
        app.include_router(router, prefix=app_settings.API_V1_STR)
    return app


async def _web_app_startup() -> None:
    await initialize_data()
