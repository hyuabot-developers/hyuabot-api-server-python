import json
from datetime import datetime
from typing import Tuple

import aioredis
import holidays
from korean_lunar_calendar import KoreanLunarCalendar

from app.hyuabot.api.core.config import settings


async def get_shuttle_term(date: datetime = datetime.now()) -> Tuple[bool, str, str]:
    """
    오늘 날짜에 대한 셔틀 운행 타입을 반환합니다.
    :param date: 날짜
    :return:
    셔틀 운행 여부(True/False),
    셔틀 운행 타입(semester, vacation, vacation_session)
    """
    redis_client = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}")
    async with redis_client.client() as connection:
        key = "shuttle_date"
        json_string: bytes = await connection.get(key)
        date_json: dict = json.loads(json_string.decode("utf-8"))

        calendar = KoreanLunarCalendar()
        calendar.setSolarDate(date.year, date.month, date.day)

        # 운행 여부 확인
        is_working = True
        if f"{date.month}/{date.day}" in date_json["halt"]["solar"]:
            is_working = False
        elif f"{calendar.lunarMonth}/{calendar.lunarDay}" in date_json["halt"]["lunar"]:
            is_working = False

        # 운행 타입 확인
        term_keys = ["semester", "vacation", "vacation_session"]
        current_term = ""
        for term_key in term_keys:
            for term in date_json[term_key]:
                start_date = datetime.strptime(term["start"], "%m/%d").replace(year=date.year)
                end_date = datetime.strptime(term["end"], "%m/%d").replace(year=date.year)

                if start_date >= end_date:
                    if date >= start_date:
                        start_date = start_date.replace(year=date.year)
                        end_date = end_date.replace(year=date.year + 1)
                    elif date <= end_date:
                        start_date = start_date.replace(year=date.year - 1)
                        end_date = end_date.replace(year=date.year)

                if start_date <= date <= end_date:
                    current_term = term_key

        if date.weekday() >= 5 or date.strftime("%Y-%m-%d") in holidays.KR():
            weekday_key = "weekends"
        else:
            weekday_key = "weekdays"
        return is_working, current_term, weekday_key
