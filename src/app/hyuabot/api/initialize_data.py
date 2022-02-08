import asyncio
import csv
import json
from datetime import datetime

import aioredis
from aiohttp import ClientSession


# 초기 서버 시작 시 셔틀 버스 정보 redis 저장
def load_shuttle_timetable():
    term_keys = ["semester", "vacation", "vacation_session"]
    day_keys = ["week", "weekend"]

    base_url = "https://raw.githubusercontent.com/hyuabot-developers/hyuabot-shuttle-timetable/main"
    tasks = []
    for term in term_keys:
        for day in day_keys:
            url = f"{base_url}/{term}/{day}.csv"
            key = f"shuttle_{term}_{day}"
            tasks.append(store_shuttle_timetable_redis(url, key))

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))


async def store_shuttle_timetable_redis(url: str, key: str):
    async with ClientSession() as session:
        async with session.get(url) as response:
            reader = csv.reader((await response.text()).splitlines(), delimiter=",")
            timetable: list[dict] = []
            for shuttle_type, shuttle_time in reader:
                timetable.append({
                    "type": shuttle_type,
                    "time": shuttle_time
                })
            redis_client = aioredis.from_url(f"redis://localhost:6379")
            await redis_client.set(key, json.dumps(timetable, ensure_ascii=False).encode("utf-8"))
