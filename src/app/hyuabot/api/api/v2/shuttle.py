from datetime import datetime

import strawberry
from korean_lunar_calendar import KoreanLunarCalendar
from sqlalchemy import and_
from sqlalchemy.orm import Session
from strawberry.types import Info

from app.hyuabot.api.models.postgresql.shuttle import ShuttleTimetable, ShuttlePeriod


@strawberry.type
class ShuttleTimetableItem:
    period: str
    weekday: str
    shuttle_type: str
    shuttle_time: str
    start_stop: str


@strawberry.type
class Shuttle:
    @strawberry.field
    def period(self, info: Info, date: str | None) -> str:
        db_session: Session = info.context["db_session"]
        if date is None:
            current_date = datetime.now()
        else:
            current_date = datetime.strptime(date, "%Y-%m-%d")

        period_item = db_session.query(ShuttlePeriod) \
            .filter(and_(
                current_date >= ShuttlePeriod.start_date,
                current_date <= ShuttlePeriod.end_date,
                ShuttlePeriod.period != "holiday",
                ShuttlePeriod.calendar_type == "solar")) \
            .order_by(ShuttlePeriod.end_date - ShuttlePeriod.start_date).first()
        if period_item is None:
            period_item = db_session.query(ShuttlePeriod) \
                .filter(and_(
                    current_date >= ShuttlePeriod.start_date,
                    current_date <= ShuttlePeriod.end_date,
                    ShuttlePeriod.calendar_type == "solar")) \
                .order_by(ShuttlePeriod.start_date - ShuttlePeriod.end_date).first()
        calendar = KoreanLunarCalendar()
        calendar.setSolarDate(current_date.year, current_date.month, current_date.day)
        lunar_period_item = db_session.query(ShuttlePeriod) \
            .filter(and_(
                calendar.LunarIsoFormat() >= ShuttlePeriod.start_date,
                calendar.LunarIsoFormat() <= ShuttlePeriod.end_date,
                ShuttlePeriod.calendar_type == "lunar",
                ShuttlePeriod.period == "halt")) \
            .order_by(ShuttlePeriod.end_date - ShuttlePeriod.start_date).first()
        if lunar_period_item is not None:
            return lunar_period_item.period
        return period_item.period

    @strawberry.field
    def weekday(self, info: Info,  date: str | None) -> str:
        db_session: Session = info.context["db_session"]
        if date is None:
            current_date = datetime.now()
        else:
            current_date = datetime.strptime(date, "%Y-%m-%d")
        period_item = db_session.query(ShuttlePeriod) \
            .filter(and_(
                current_date >= ShuttlePeriod.start_date,
                current_date <= ShuttlePeriod.end_date,
                ShuttlePeriod.period == "holiday",
                ShuttlePeriod.calendar_type == "solar")) \
            .order_by(ShuttlePeriod.end_date - ShuttlePeriod.start_date).first()

        calendar = KoreanLunarCalendar()
        calendar.setSolarDate(current_date.year, current_date.month, current_date.day)
        lunar_period_item = db_session.query(ShuttlePeriod) \
            .filter(and_(
                calendar.LunarIsoFormat() >= ShuttlePeriod.start_date,
                calendar.LunarIsoFormat() <= ShuttlePeriod.end_date,
                ShuttlePeriod.calendar_type == "lunar",
                ShuttlePeriod.period == "holiday")) \
            .order_by(ShuttlePeriod.end_date - ShuttlePeriod.start_date).first()

        if period_item is not None or lunar_period_item is not None or now.weekday() >= 5:
            return "weekends"
        return "weekdays"

    @strawberry.field
    def timetable(
            self, info: Info, period: str | None, weekday: str | None, shuttle_type: str | None,
            start_stop: str | None, start_time: str | None, end_time: str | None, count: int = 999,
    ) -> list[ShuttleTimetableItem]:
        db_session: Session = info.context["db_session"]
        expressions = []
        if weekday == "now":
            weekday = "weekdays" if datetime.now().weekday() < 5 else "weekends"
        if weekday is not None:
            expressions.append(ShuttleTimetable.weekday == weekday)
        if period is not None:
            expressions.append(ShuttleTimetable.period == period)
        if shuttle_type is not None:
            expressions.append(ShuttleTimetable.shuttle_type == shuttle_type)
        if start_stop is not None:
            expressions.append(ShuttleTimetable.start_stop == start_stop)
        if start_time is not None:
            expressions.append(ShuttleTimetable.start_time == start_time)
        if end_time is not None:
            expressions.append(ShuttleTimetable.end_time == end_time)

        query = db_session.query(ShuttleTimetable) \
            .filter(and_(True, *expressions)).limit(count)
        result: list[ShuttleTimetableItem] = []
        for x in query:  # type: ShuttleTimetable
            result.append(
                ShuttleTimetableItem(
                    period=x.period,
                    weekday=x.weekday,
                    shuttle_type=x.shuttle_type,
                    shuttle_time=x.shuttle_time,
                    start_stop=x.start_stop,
                ),
            )
        return result
