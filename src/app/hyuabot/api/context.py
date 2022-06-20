from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple

from fastapi import FastAPI
from sqlalchemy.engine import Engine

if TYPE_CHECKING:
    from app.hyuabot.api.core.config import AppSettings


class AppContext(NamedTuple):
    app_settings: AppSettings
    db_engine: Engine

    @staticmethod
    def from_app(app: FastAPI) -> AppContext:
        try:
            return app.extra['app_context']  # type: ignore
        except KeyError:
            raise RuntimeError('App context is not initialized')
