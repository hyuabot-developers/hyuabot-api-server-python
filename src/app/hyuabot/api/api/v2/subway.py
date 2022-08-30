import datetime
from typing import Optional

import strawberry
from sqlalchemy import and_
from sqlalchemy.orm import Session
from strawberry.types import Info

from app.hyuabot.api.models.postgresql.subway import SubwayTimetable, SubwayRealtime


@strawberry.type
class SubwayTimetableItem:
    heading: str
    weekday: str
    terminal_station: str
    departure_time: str


@strawberry.type
class SubwayRealtimeItem:
    heading: str
    update_time: str
    train_number: str
    last_train: str
    terminal_station: str
    current_station: str
    remained_time: str
    status: str


@strawberry.type
class SubwayItem:
    station_name: str
    route_name: str

    @strawberry.field
    def timetable(self,
                  info: Info, heading: Optional[str] = None, weekday: Optional[str] = None,
                  start_time: Optional[datetime.time] = None, end_time: Optional[datetime.time] = None,
                  count: int = 999) -> list[SubwayTimetableItem]:
        db_session: Session = info.context["db_session"]
        expressions = [
            SubwayTimetable.route_name == self.route_name,
            SubwayTimetable.station_name == self.station_name,
        ]
        if weekday == "now":
            weekday = "weekdays" if datetime.datetime.now().weekday() < 5 else "weekends"
        if weekday is not None:
            expressions.append(SubwayTimetable.weekday == weekday)
        if heading is not None:
            expressions.append(SubwayTimetable.heading == heading)
        if start_time is not None:
            expressions.append(SubwayTimetable.departure_time >= start_time)
        if end_time is not None:
            expressions.append(SubwayTimetable.departure_time <= end_time)

        query = db_session.query(SubwayTimetable)\
            .filter(and_(True, *expressions)).order_by(SubwayTimetable.departure_time).limit(count)
        result: list[SubwayTimetableItem] = []
        for x in query:
            result.append(SubwayTimetableItem(
                heading=x.heading,
                weekday=x.weekday,
                terminal_station=x.terminal_station,
                departure_time=x.departure_time,
            ))
        return result

    @strawberry.field
    def realtime(self, info: Info, heading: Optional[str] = None) -> list[SubwayRealtimeItem]:
        db_session: Session = info.context["db_session"]
        query = db_session.query(SubwayRealtime).filter(and_(
            SubwayRealtime.station_name == self.station_name,
            SubwayRealtime.route_name == self.route_name,
            SubwayRealtime.heading == heading if heading else True,
        )).order_by(SubwayRealtime.remained_time).all()
        result: list[SubwayRealtimeItem] = []
        for x in query:
            result.append(SubwayRealtimeItem(
                heading=x.heading,
                update_time=x.update_time,
                train_number=x.train_number,
                last_train=x.last_train,
                terminal_station=x.terminal_station,
                current_station=x.current_station,
                remained_time=x.remained_time,
                status=x.status,
            ))
        return result
