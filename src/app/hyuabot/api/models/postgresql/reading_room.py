from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql import sqltypes

from app.hyuabot.api.models.postgresql import BaseModel


class ReadingRoom(BaseModel):
    __tablename__ = 'reading_room'
    room_name = Column(sqltypes.String, primary_key=True)
    campus_id = Column(sqltypes.String, ForeignKey('campus.campus_id'), primary_key=True)
    is_active = Column(sqltypes.Boolean)
    is_reservable = Column(sqltypes.Boolean)
    total_seat = Column(sqltypes.Integer)
    active_seat = Column(sqltypes.Integer)
    occupied_seat = Column(sqltypes.Integer)
    available_seat = Column(sqltypes.Integer)
