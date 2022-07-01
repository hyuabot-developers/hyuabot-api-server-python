__version__ = "1.0.0-alpha1"

import functools

import strawberry
from fastapi import FastAPI, Depends
from fastapi.middleware.gzip import GZipMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy_utils import database_exists, create_database, drop_database
from starlette.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter

from .api.v1 import API_V1_ROUTERS
from .api.v2 import Query
from .context import AppContext
from .core.config import AppSettings
from .core.fetch import fetch_router
from .initialize_data import initialize_data
from .models.postgresql import BaseModel
from .utlis.fastapi import get_db_session


async def get_context(db_session=Depends(get_db_session)):
    return {"db_session": db_session}


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

    schema = strawberry.Schema(Query)
    graphql_app = GraphQLRouter(schema, context_getter=get_context)
    app.include_router(graphql_app, prefix=app_settings.API_V2_STR)

    app.include_router(fetch_router)
    return app


async def _web_app_startup(app: FastAPI, app_settings: AppSettings) -> None:
    db_engine = create_engine(app_settings.DATABASE_URI, **app_settings.DATABASE_OPTIONS)
    if database_exists(app_settings.DATABASE_URI):
        drop_database(app_settings.DATABASE_URI)
    create_database(app_settings.DATABASE_URI)
    try:
        BaseModel.metadata.create_all(db_engine)
    except Exception as e:
        print(e)
    app_context = AppContext(app_settings, db_engine)
    app.extra["app_context"] = app_context

    db_session = Session(db_engine)
    await initialize_data(db_session)
    db_session.close()


async def _web_app_shutdown(app: FastAPI) -> None:
    app_context = AppContext.from_app(app)
    app_context.db_engine.dispose()
