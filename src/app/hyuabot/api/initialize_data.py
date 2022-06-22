import asyncio
import csv
import json

from aiohttp import ClientSession
from aioredis import Redis

# 초기 서버 시작 시 셔틀 버스 정보 redis 저장
from app.hyuabot.api.core.database import get_redis_connection, set_redis_value
from app.hyuabot.api.core.fetch.bus import fetch_bus_realtime_in_a_row
from app.hyuabot.api.core.fetch.reading_room import fetch_reading_room_api, fetch_reading_room
from app.hyuabot.api.core.fetch.subway import fetch_subway_realtime_information


async def load_shuttle_timetable():
    redis_connection = await get_redis_connection("shuttle")

    term_keys = ["semester", "vacation", "vacation_session"]
    day_keys = ["week", "weekend"]
    day_dict = {"week": "weekdays", "weekend": "weekends"}

    base_url = "https://raw.githubusercontent.com/hyuabot-developers/hyuabot-shuttle-timetable/main"
    tasks = []
    for term in term_keys:
        for day in day_keys:
            url = f"{base_url}/{term}/{day}.csv"
            key = f"shuttle_{term}_{day_dict[day]}"
            tasks.append(store_shuttle_timetable_redis(redis_connection, url, key))

    await asyncio.gather(*tasks)
    await redis_connection.close()


async def store_shuttle_timetable_redis(redis_connection: Redis, url: str, key: str):
    async with ClientSession() as session:
        async with session.get(url) as response:
            reader = csv.reader((await response.text()).splitlines(), delimiter=",")
            timetable: list[dict] = []
            for shuttle_type, shuttle_time, shuttle_start_stop in reader:
                timetable.append({
                    "type": shuttle_type,
                    "time": shuttle_time,
                    "startStop": shuttle_start_stop,
                })
            await set_redis_value(redis_connection, key,
                                  json.dumps(timetable, ensure_ascii=False).encode("utf-8"))


async def store_shuttle_date_redis():
    redis_connection = await get_redis_connection("shuttle")

    url = "https://raw.githubusercontent.com/hyuabot-developers/hyuabot-shuttle-timetable/main/date.json"
    key = "shuttle_date"

    async with ClientSession() as session:
        async with session.get(url) as response:
            date = json.loads(await response.text())
            await set_redis_value(redis_connection, key,
                                  json.dumps(date, ensure_ascii=False).encode("utf-8"))
    await redis_connection.close()


# 초기 서버 시작 시 노선 버스 정보 redis 저장
async def load_bus_timetable():
    redis_connection = await get_redis_connection("bus")

    day_keys = ["weekdays", "saturday", "sunday"]
    line_keys = ["10-1", "707-1", "3102"]

    base_url = "https://raw.githubusercontent.com/hyuabot-developers/hyuabot-bus-timetable/main"
    tasks = []
    for line in line_keys:
        for day in day_keys:
            url = f"{base_url}/{line}/{day}/timetable.csv"
            key = f"bus_{line}_{day}"
            tasks.append(store_bus_timetable_redis(redis_connection.client(), url, key))

    await asyncio.gather(*tasks)
    await redis_connection.close()


async def store_bus_timetable_redis(redis_connection: Redis, url: str, key: str):
    async with ClientSession() as session:
        async with session.get(url) as response:
            reader = csv.reader((await response.text()).splitlines(), delimiter=",")
            timetable: list[str] = []
            for bus_arrival_time in reader:
                timetable.append(bus_arrival_time[0])
            await set_redis_value(redis_connection, key,
                                  json.dumps(timetable, ensure_ascii=False).encode("utf-8"))


# 초기 서버 시작 시 전철 출발 정보 redis 저장
async def load_subway_timetable():
    redis_connection = await get_redis_connection("subway")
    line_keys = [("skyblue", "1004"), ("yellow", "1075")]
    day_keys = ["weekdays", "weekends"]
    heading_keys = ["up", "down"]

    base_url = "https://raw.githubusercontent.com/hyuabot-developers/hyuabot-subway-timetable/main"
    tasks = []
    for line, line_id in line_keys:
        for day in day_keys:
            for heading in heading_keys:
                url = f"{base_url}/{line}/{day}/{heading}.csv"
                key = f"subway_{line_id}_{day}_{heading}"
                tasks.append(store_subway_timetable_redis(redis_connection, url, key))

    await asyncio.gather(*tasks)
    await redis_connection.close()


async def store_subway_timetable_redis(redis_connection: Redis, url: str, key: str):
    async with ClientSession() as session:
        async with session.get(url) as response:
            reader = csv.reader((await response.text()).splitlines(), delimiter=",")
            timetable: list[dict] = []
            for terminate_station, departure_time in reader:
                timetable.append({
                    "terminalStation": terminate_station,
                    "departureTime": departure_time,
                })
            await set_redis_value(redis_connection, key,
                                  json.dumps(timetable, ensure_ascii=False).encode("utf-8"))


async def initialize_data():
    tasks = {
        load_shuttle_timetable(),
        store_shuttle_date_redis(),
        load_bus_timetable(),
        load_subway_timetable(),
        fetch_reading_room_api("seoul", 1),
        fetch_reading_room_api("erica", 2),
        fetch_bus_realtime_in_a_row(),
        fetch_reading_room(),
        fetch_subway_realtime_information(),
    }
    await asyncio.gather(*tasks)
