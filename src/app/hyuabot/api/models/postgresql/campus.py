from sqlalchemy import Column
from sqlalchemy.sql import sqltypes

from app.hyuabot.api.models.postgresql import BaseModel


class Campus(BaseModel):
    __tablename__ = 'campus'
    campus_name = Column(sqltypes.String)
    campus_id = Column(sqltypes.Integer, primary_key=True)
