from datetime import time, datetime
from typing import Optional

import strawberry
from sqlalchemy import and_
from sqlalchemy.orm import Session
from strawberry.types import Info

from app.hyuabot.api.models.postgresql.bus import BusTimetable, BusRealtime


@strawberry.type
class BusTimetableItem:
    departure_time: time
    weekday: str


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
    def timetable(self, info: Info, weekday: Optional[str] = None, count: int = 999) -> list[BusTimetableItem]:
        db_session: Session = info.context["db_session"]
        expressions = [BusTimetable.route_id == self.route_id]
        if weekday == "now":
            weekday = "weekdays" if datetime.now().weekday() < 5 else "weekends"
        if weekday is not None and len(weekday) > 0:
            expressions.append(BusTimetable.weekday == weekday)
        query = db_session.query(BusTimetable).filter(and_(True, *expressions)).limit(count)
        result: list[BusTimetableItem] = []
        for x in query:
            result.append(BusTimetableItem(
                departure_time=x.departure_time,
                weekday=x.weekday,
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
