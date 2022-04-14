__version__ = "1.0.0-alpha1"

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.hyuabot.api.api.api_v1 import API_V1_ROUTERS
from app.hyuabot.api.core.config import AppSettings
from app.hyuabot.api.core.fetch import fetch_router
from app.hyuabot.api.initialize_data import initialize_data


def create_app(app_settings: AppSettings) -> FastAPI:
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_event_handler("startup", _web_app_startup)

    app.extra["settings"] = app_settings
    for router in API_V1_ROUTERS:
        app.include_router(router, prefix=app_settings.API_V1_STR)
    app.include_router(fetch_router)
    return app


async def _web_app_startup() -> None:
    await initialize_data()
