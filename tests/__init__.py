from sqlalchemy.orm import Session
from sqlalchemy_utils import database_exists, drop_database, create_database

from app.hyuabot.api import AppSettings
from app.hyuabot.api.models.postgresql import BaseModel


def get_database_session(app_settings: AppSettings) -> Session:
    from sqlalchemy import create_engine
    db_engine = create_engine(app_settings.DATABASE_URI, **app_settings.DATABASE_OPTIONS)
    if database_exists(app_settings.DATABASE_URI):
        drop_database(app_settings.DATABASE_URI)
    create_database(app_settings.DATABASE_URI)
    try:
        BaseModel.metadata.create_all(db_engine)
        return Session(db_engine)
    except Exception as e:
        print(e)
