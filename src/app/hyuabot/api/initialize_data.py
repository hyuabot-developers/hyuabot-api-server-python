import asyncio
import csv
import json

import aioredis
from aiohttp import ClientSession

from .core.config import settings


# 초기 서버 시작 시 셔틀 버스 정보 redis 저장
async def load_shuttle_timetable():
    term_keys = ["semester", "vacation", "vacation_session"]
    day_keys = ["week", "weekend"]
    day_dict = {"week": "weekdays", "weekend": "weekends"}

    base_url = "https://raw.githubusercontent.com/hyuabot-developers/hyuabot-shuttle-timetable/main"
    tasks = []
    for term in term_keys:
        for day in day_keys:
            url = f"{base_url}/{term}/{day}.csv"
            key = f"shuttle_{term}_{day_dict[day]}"
            tasks.append(store_shuttle_timetable_redis(url, key))

    await asyncio.gather(*tasks)


async def store_shuttle_timetable_redis(url: str, key: str):
    redis_client = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}")
    async with ClientSession() as session:
        async with session.get(url) as response:
            reader = csv.reader((await response.text()).splitlines(), delimiter=",")
            timetable: list[dict] = []
            for shuttle_type, shuttle_time in reader:
                timetable.append({
                    "type": shuttle_type,
                    "time": shuttle_time,
                })
            async with redis_client.client() as connection:
                await connection.set(key, json.dumps(timetable, ensure_ascii=False).encode("utf-8"))


async def store_shuttle_date_redis():
    url = "https://raw.githubusercontent.com/hyuabot-developers/hyuabot-shuttle-timetable/main/date.json"
    key = "shuttle_date"

    redis_client = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}")
    async with ClientSession() as session:
        async with session.get(url) as response:
            date = json.loads(await response.text())
            async with redis_client.client() as connection:
                await connection.set(key, json.dumps(date, ensure_ascii=False).encode("utf-8"))


# 초기 서버 시작 시 노선 버스 정보 redis 저장
async def load_bus_timetable():
    day_keys = ["weekdays", "saturday", "sunday"]
    line_keys = ["10-1", "707-1", "3102"]

    base_url = "https://raw.githubusercontent.com/hyuabot-developers/hyuabot-bus-timetable/main"
    tasks = []
    for line in line_keys:
        for day in day_keys:
            url = f"{base_url}/{line}/{day}/timetable.csv"
            key = f"bus_{line}_{day}"
            tasks.append(store_bus_timetable_redis(url, key))

    await asyncio.gather(*tasks)


async def store_bus_timetable_redis(url: str, key: str):
    redis_client = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}")
    async with ClientSession() as session:
        async with session.get(url) as response:
            reader = csv.reader((await response.text()).splitlines(), delimiter=",")
            timetable: list[str] = []
            for bus_arrival_time in reader:
                timetable.append(bus_arrival_time[0])
            async with redis_client.client() as connection:
                await connection.set(key, json.dumps(timetable, ensure_ascii=False).encode("utf-8"))


# 초기 서버 시작 시 전철 출발 정보 redis 저장
async def load_subway_timetable():
    line_keys = ["skyblue", "yellow"]
    day_keys = ["weekdays", "weekends"]
    heading_keys = ["up", "down"]

    base_url = "https://raw.githubusercontent.com/hyuabot-developers/hyuabot-subway-timetable/main"
    tasks = []
    for line in line_keys:
        for day in day_keys:
            for heading in heading_keys:
                url = f"{base_url}/{line}/{day}/{heading}.csv"
                key = f"subway_{line}_{day}_{heading}"
                tasks.append(store_subway_timetable_redis(url, key))

    await asyncio.gather(*tasks)


async def store_subway_timetable_redis(url: str, key: str):
    redis_client = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}")
    async with ClientSession() as session:
        async with session.get(url) as response:
            reader = csv.reader((await response.text()).splitlines(), delimiter=",")
            timetable: list[dict] = []
            for terminate_station, departure_time in reader:
                timetable.append({
                    "terminalStation": terminate_station,
                    "departureTime": departure_time,
                })
            async with redis_client.client() as connection:
                await connection.set(key, json.dumps(timetable, ensure_ascii=False).encode("utf-8"))


async def initialize_data():
    await load_shuttle_timetable()
    await store_shuttle_date_redis()
    await load_bus_timetable()
    await load_subway_timetable()
