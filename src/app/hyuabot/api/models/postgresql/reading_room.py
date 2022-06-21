from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql import sqltypes

from app.hyuabot.api.models.postgresql import BaseModel


class ReadingRoom(BaseModel):
    __tablename__ = 'reading_room'
    room_name = Column(sqltypes.String, primary_key=True)
    campus_id = Column(sqltypes.Integer, ForeignKey('campus.campus_id'), primary_key=True)
    is_active = Column(sqltypes.Boolean, default=True)
    is_reservable = Column(sqltypes.Boolean, default=True)
    total_seat = Column(sqltypes.Integer, default=0)
    active_seat = Column(sqltypes.Integer, default=0)
    occupied_seat = Column(sqltypes.Integer, default=0)
    available_seat = Column(sqltypes.Integer, default=0)
