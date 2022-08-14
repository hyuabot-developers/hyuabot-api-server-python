from datetime import datetime, timezone, timedelta
from typing import Tuple

import holidays
from korean_lunar_calendar import KoreanLunarCalendar
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.hyuabot.api.models.postgresql.shuttle import ShuttlePeriod

korea_standard_time = timezone(timedelta(hours=9))


async def get_shuttle_term(db_session: Session, date_item: datetime = None) \
        -> Tuple[bool, str, str, str]:
    """
    오늘 날짜에 대한 셔틀 운행 타입을 반환합니다.
    :param db_session:
    :param date_item:
    :return:
    셔틀 운행 여부(True/False),
    셔틀 운행 타입(semester, vacation, vacation_session)
    """
    if date_item is None:
        date_item = datetime.now(tz=korea_standard_time)

    calendar = KoreanLunarCalendar()
    calendar.setSolarDate(date_item.year, date_item.month, date_item.day)
    period_item = db_session.query(ShuttlePeriod)\
        .filter(and_(
            date_item >= ShuttlePeriod.start_date,
            date_item <= ShuttlePeriod.end_date,
            ShuttlePeriod.calendar_type == "solar"))\
        .order_by(ShuttlePeriod.end_date - ShuttlePeriod.start_date).first()
    if period_item is None:
        return True, "semester", "weekays", date_item.strftime("%Y-%m-%d %H:%M:%S")

    # 운행 여부 확인
    is_working = True
    if period_item.period == "halt":
        is_working = False

    lunar_period_item = db_session.query(ShuttlePeriod)\
        .filter(and_(
            calendar.LunarIsoFormat() >= ShuttlePeriod.start_date,
            calendar.LunarIsoFormat() <= ShuttlePeriod.end_date,
            ShuttlePeriod.calendar_type == "lunar",
            ShuttlePeriod.period == "halt"))\
        .order_by(ShuttlePeriod.end_date - ShuttlePeriod.start_date).first()
    if lunar_period_item is not None:
        is_working = False

    if date_item.weekday() >= 5 or date_item.strftime("%Y-%m-%d") in holidays.KR():
        weekday_key = "weekends"
    else:
        weekday_key = "weekdays"
    return is_working, period_item.period, weekday_key, date_item.strftime("%Y-%m-%d %H:%M:%S")
