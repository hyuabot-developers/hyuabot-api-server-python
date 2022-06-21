from sqlalchemy import Column
from sqlalchemy.sql import sqltypes

from app.hyuabot.api.models.postgresql import BaseModel


class Campus(BaseModel):
    __tablename__ = 'campus'
    campus_name = Column(sqltypes.String, primary_key=True)
    campus_id = Column(sqltypes.Integer)
