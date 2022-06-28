from sqlalchemy import Column, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.sql import sqltypes

from app.hyuabot.api.models.postgresql import BaseModel


class SubwayRoute(BaseModel):
    __tablename__ = 'subway_route'
    route_name = Column(sqltypes.String, primary_key=True)
    route_id = Column(sqltypes.Integer)


class SubwayStation(BaseModel):
    __tablename__ = 'subway_station'
    station_name = Column(sqltypes.String, primary_key=True)


class SubwayRealtime(BaseModel):
    __tablename__ = 'subway_realtime'
    __table_args__ = (
        PrimaryKeyConstraint('station_name', 'route_name', 'train_number'),
    )
    route_name = Column(sqltypes.String, ForeignKey('subway_route.route_name'))
    station_name = Column(sqltypes.String, ForeignKey('subway_station.station_name'))
    heading = Column(sqltypes.String)
    update_time = Column(sqltypes.DateTime)
    train_number = Column(sqltypes.String)
    last_train = Column(sqltypes.Boolean)
    terminal_station = Column(sqltypes.String)
    current_station = Column(sqltypes.String)
    remained_time = Column(sqltypes.Integer)
    status = Column(sqltypes.String)


class SubwayTimetable(BaseModel):
    __tablename__ = 'subway_timetable'
    __table_args__ = (
        PrimaryKeyConstraint('route_name', 'weekday', 'heading', 'departure_time'),
    )
    route_name = Column(sqltypes.String, ForeignKey('subway_route.route_name'))
    station_name = Column(sqltypes.String, ForeignKey('subway_station.station_name'))
    heading = Column(sqltypes.String)
    weekday = Column(sqltypes.String)
    terminal_station = Column(sqltypes.String)
    departure_time = Column(sqltypes.Time)
