from datetime import time

import strawberry
from sqlalchemy import and_
from sqlalchemy.orm import Session
from strawberry.types import Info

from app.hyuabot.api.models.postgresql.subway import SubwayTimetable, SubwayRealtime


@strawberry.type
class SubwayTimetableItem:
    route_name: str
    station_name: str
    heading: str
    weekday: str
    terminal_station: str
    departure_time: str


@strawberry.type
class SubwayRealtimeItem:
    route_name: str
    station_name: str
    heading: str
    update_time: str
    train_number: str
    last_train: str
    terminal_station: str
    current_station: str
    remained_time: str
    status: str


@strawberry.type
class Subway:
    realtime: list[SubwayRealtimeItem]
    timetable: list[SubwayTimetableItem]

    @strawberry.field
    def timetable(
            self, info: Info, route_name: str = None, station_name: str = None, heading: str = None,
            weekday: str = None, terminal_station: str = None,
            start_time: time = None, end_time: time = None
    ) -> list[SubwayTimetableItem]:
        db_session: Session = info.context["db_session"]

        query = db_session.query(SubwayTimetable) \
            .filter(and_(
            SubwayTimetable.route_name == route_name if route_name else True,
            SubwayTimetable.station_name == station_name if station_name else True,
            SubwayTimetable.heading == heading if heading else True,
            SubwayTimetable.weekday == weekday if weekday else True,
            SubwayTimetable.terminal_station >= terminal_station if terminal_station else True,
            SubwayTimetable.departure_time >= start_time if start_time else True,
            SubwayTimetable.departure_time <= end_time if end_time else True,
        )).all()
        result: list[SubwayTimetableItem] = []
        for x in query:  # type: SubwayTimetable
            result.append(
                SubwayTimetableItem(
                    route_name=x.route_name,
                    station_name=x.station_name,
                    heading=x.heading,
                    weekday=x.weekday,
                    terminal_station=x.terminal_station,
                    departure_time=x.departure_time,
                )
            )
        return result

    @strawberry.field
    def realtime(
            self, info: Info, route_name: str = None, station_name: str = None, heading: str = None
    ) -> list[SubwayRealtimeItem]:
        db_session: Session = info.context["db_session"]

        query = db_session.query(SubwayRealtime) \
            .filter(and_(
                SubwayRealtime.route_name == route_name if route_name else True,
                SubwayRealtime.station_name == station_name if station_name else True,
                SubwayRealtime.heading == heading if heading else SubwayRealtime.heading != "",
            )).all()
        result: list[SubwayRealtimeItem] = []
        for x in query:  # type: SubwayRealtime
            result.append(
                SubwayRealtimeItem(
                    route_name=x.route_name,
                    station_name=x.station_name,
                    heading=x.heading,
                    update_time=x.update_time,
                    train_number=x.train_number,
                    last_train=x.last_train,
                    terminal_station=x.terminal_station,
                    current_station=x.current_station,
                    remained_time=x.remained_time,
                    status=x.status,
                )
            )
        return result
