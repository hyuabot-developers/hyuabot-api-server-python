from sqlalchemy import Column, PrimaryKeyConstraint
from sqlalchemy.sql import sqltypes

from app.hyuabot.api.models.postgresql import BaseModel


class ShuttlePeriod(BaseModel):
    __tablename__ = 'shuttle_period'
    __table_args__ = (
        PrimaryKeyConstraint('period', 'start_date', 'calendar_type'),
    )
    period = Column(sqltypes.String)
    start_date = Column(sqltypes.DateTime)
    end_date = Column(sqltypes.DateTime)
    calendar_type = Column(sqltypes.String, default='solar')


class ShuttleTimetable(BaseModel):
    __tablename__ = 'shuttle_timetable'
    period = Column(sqltypes.String, primary_key=True)
    weekday = Column(sqltypes.String, primary_key=True)
    shuttle_type = Column(sqltypes.String, primary_key=True)
    shuttle_time = Column(sqltypes.Time, primary_key=True)
    start_stop = Column(sqltypes.String, primary_key=True)
