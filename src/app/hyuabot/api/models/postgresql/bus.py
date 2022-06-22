from sqlalchemy import Column, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.sql import sqltypes

from app.hyuabot.api.models.postgresql import BaseModel


class BusRoute(BaseModel):
    __tablename__ = 'bus_route'
    route_name = Column(sqltypes.String)
    gbis_id = Column(sqltypes.Integer, primary_key=True)
    start_stop = Column(sqltypes.String)
    terminal_stop = Column(sqltypes.String)
    time_from_start_stop = Column(sqltypes.Integer)


class BusStop(BaseModel):
    __tablename__ = 'bus_stop'
    stop_name = Column(sqltypes.String)
    gbis_id = Column(sqltypes.Integer, primary_key=True)


class BusRealtime(BaseModel):
    __tablename__ = 'bus_realtime'
    __table_args__ = (
        PrimaryKeyConstraint('route_id', 'stop_id', 'remained_time'),
    )
    route_id = Column(sqltypes.Integer, ForeignKey('bus_route.gbis_id'))
    stop_id = Column(sqltypes.Integer, ForeignKey('bus_stop.gbis_id'))
    low_plate = Column(sqltypes.Boolean)
    remained_stop = Column(sqltypes.Integer)
    remained_time = Column(sqltypes.Integer)
    remained_seat = Column(sqltypes.Integer)


class BusTimetable(BaseModel):
    __tablename__ = 'bus_timetable'
    __table_args__ = (
        PrimaryKeyConstraint('route_id', 'weekday', 'departure_time'),
    )
    route_id = Column(sqltypes.Integer, ForeignKey('bus_route.gbis_id'))
    weekday = Column(sqltypes.String)
    departure_time = Column(sqltypes.Time)
