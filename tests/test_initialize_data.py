import json
import re

import pytest

from app.hyuabot.api.core.database import get_redis_connection
from app.hyuabot.api.initialize_data import load_shuttle_timetable, store_shuttle_date_redis, \
    load_bus_timetable, load_subway_timetable


@pytest.mark.asyncio
async def test_store_shuttle_timetable():
    term_keys = ["semester", "vacation", "vacation_session"]
    day_keys = ["weekdays", "weekends"]

    await load_shuttle_timetable()

    redis_connection = await get_redis_connection("shuttle")
    async with redis_connection.client() as connection:
        for term in term_keys:
            for day in day_keys:
                key = f"shuttle_{term}_{day}"
                json_string: bytes = await connection.get(key)
                timetable: list[dict] = json.loads(json_string.decode("utf-8"))

                assert len(timetable) > 0
                for shuttle_time in timetable:
                    assert "time" in shuttle_time.keys()
                    assert "type" in shuttle_time.keys()

                    assert ":" in shuttle_time["time"]
                    hour, minute = shuttle_time["time"].split(":")
                    assert 0 <= int(hour) < 24
                    assert 0 <= int(minute) < 60

                    assert shuttle_time["type"] in ["DH", "DY", "C"]
    await redis_connection.close()


@pytest.mark.asyncio
async def test_store_shuttle_date():
    date_regex = re.compile(r"^\d{1,2}/\d{1,2}$")
    await store_shuttle_date_redis()

    redis_connection = await get_redis_connection("shuttle")
    async with redis_connection.client() as connection:
        key = "shuttle_date"
        json_string: bytes = await connection.get(key)
        date_json: dict = json.loads(json_string.decode("utf-8"))

        for key in date_json.keys():
            if key == "holiday":
                assert all([date_regex.match(date) for date in date_json[key]])
            elif key == "halt":
                for calendar_type in date_json[key].keys():
                    assert all([date_regex.match(date) for date in date_json[key][calendar_type]])
            else:
                for term in date_json[key]:
                    assert "key" in term.keys()
                    assert "start" in term.keys()
                    assert "end" in term.keys()

                    assert date_regex.match(term["start"])
                    assert date_regex.match(term["end"])
    await redis_connection.close()


@pytest.mark.asyncio
async def test_store_bus_timetable():
    day_keys = ["weekdays", "saturday", "sunday"]
    line_keys = ["10-1", "707-1", "3102"]
    await load_bus_timetable()

    redis_connection = await get_redis_connection("bus")
    async with redis_connection.client() as connection:
        for line in line_keys:
            for day in day_keys:
                key = f"bus_{line}_{day}"
                json_string: bytes = await connection.get(key)
                timetable: list[str] = json.loads(json_string.decode("utf-8"))

                assert len(timetable) > 0
                for bus_time in timetable:
                    assert ":" in bus_time
                    hour, minute = bus_time.split(":")
                    assert 0 <= int(hour) < 24
                    assert 0 <= int(minute) < 60
    await redis_connection.close()


@pytest.mark.asyncio
async def test_store_subway_timetable():
    line_keys = ["1004", "1075"]
    day_keys = ["weekdays", "weekends"]
    heading_keys = ["up", "down"]
    await load_subway_timetable()

    redis_connection = await get_redis_connection("subway")
    async with redis_connection.client() as connection:
        for line_id in line_keys:
            for day in day_keys:
                for heading in heading_keys:
                    key = f"subway_{line_id}_{day}_{heading}"
                    json_string: bytes = await connection.get(key)
                    timetable: list[dict] = json.loads(json_string.decode("utf-8"))

                    assert len(timetable) > 0
                    for subway_item in timetable:
                        assert "terminalStation" in subway_item.keys()
                        assert "departureTime" in subway_item.keys()

                        assert ":" in subway_item["departureTime"]
                        hour, minute, seconds = subway_item["departureTime"].split(":")
                        assert 0 <= int(hour) < 24
                        assert 0 <= int(minute) < 60
                        assert 0 <= int(seconds) < 60
    await redis_connection.close()
