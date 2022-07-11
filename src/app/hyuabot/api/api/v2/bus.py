from datetime import time, datetime

import strawberry
from sqlalchemy import and_
from sqlalchemy.orm import Session
from strawberry.types import Info

from app.hyuabot.api.models.postgresql.bus import BusTimetable, BusRealtime


@strawberry.type
class BusTimetableItem:
    departure_time: time


@strawberry.type
class BusRealtimeItem:
    low_floor: bool
    remained_stop: int
    remained_time: int
    remained_seat: int


@strawberry.type
class BusItem:
    stop_name: str
    route_name: str
    stop_id: int
    route_id: int
    start_stop: str
    terminal_stop: str
    time_from_start_stop: int

    @strawberry.field
    def timetable(self, info: Info, weekday: str) -> list[BusTimetableItem]:
        db_session: Session = info.context["db_session"]
        if weekday == "now":
            weekday = "weekdays" if datetime.now().weekday() < 5 else "weekends"
        query = db_session.query(BusTimetable).filter(and_(
            BusTimetable.route_id == self.route_id,
            BusTimetable.weekday == weekday if weekday else True,
        )).all()
        result: list[BusTimetableItem] = []
        for x in query:
            result.append(BusTimetableItem(
                departure_time=x.departure_time,
            ))
        return result

    @strawberry.field
    def realtime(self, info: Info) -> list[BusRealtimeItem]:
        db_session: Session = info.context["db_session"]
        query = db_session.query(BusRealtime).filter(and_(
            BusRealtime.route_id == self.route_id,
            BusRealtime.stop_id == self.stop_id,
        )).all()
        result: list[BusRealtimeItem] = []
        for x in query:  # type: BusRealtime
            result.append(BusRealtimeItem(
                low_floor=x.low_plate,
                remained_stop=x.remained_stop,
                remained_time=x.remained_time,
                remained_seat=x.remained_seat,
            ))
        return result
