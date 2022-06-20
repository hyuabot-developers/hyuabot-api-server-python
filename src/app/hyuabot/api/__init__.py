__version__ = "1.0.0-alpha1"

import functools

from fastapi import FastAPI
from sqlalchemy import create_engine
from starlette.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.hyuabot.api.api.api_v1 import API_V1_ROUTERS
from app.hyuabot.api.context import AppContext
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
    app.add_event_handler("startup",
                          functools.partial(_web_app_startup, app=app, app_settings=app_settings))
    app.add_event_handler("shutdown", functools.partial(_web_app_shutdown, app=app))

    app.extra["settings"] = app_settings
    for router in API_V1_ROUTERS:
        app.include_router(router, prefix=app_settings.API_V1_STR)
    app.include_router(fetch_router)
    return app


async def _web_app_startup(app: FastAPI, app_settings: AppSettings) -> None:
    db_engine = create_engine(app_settings.DATABASE_URI, **app_settings.DATABASE_OPTIONS)
    app_context = AppContext(app_settings, db_engine)
    app.extra["app_context"] = app_context
    await initialize_data()


async def _web_app_shutdown(app: FastAPI) -> None:
    app_context = AppContext.from_app(app)
    app_context.db_engine.dispose()
