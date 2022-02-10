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

    base_url = "https://raw.githubusercontent.com/hyuabot-developers/hyuabot-shuttle-timetable/main"
    tasks = []
    for term in term_keys:
        for day in day_keys:
            url = f"{base_url}/{term}/{day}.csv"
            key = f"shuttle_{term}_{day}"
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
