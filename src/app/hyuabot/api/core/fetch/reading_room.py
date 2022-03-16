import asyncio
import json
from datetime import datetime

import aiohttp
from fastapi import APIRouter
from starlette.responses import JSONResponse

from app.hyuabot.api.core.database import get_redis_connection, set_redis_value
from app.hyuabot.api.core.date import korea_standard_time

fetch_reading_room_router = APIRouter(prefix="/library")
campus_id_dict = {
    "seoul": 1,
    "erica": 2,
}


@fetch_reading_room_router.get("", status_code=200)
async def fetch_reading_room() -> JSONResponse:
    tasks = []
    for campus_name, campus_id in campus_id_dict.items():
        tasks.append(fetch_reading_room_api(campus_name, campus_id))
    await asyncio.gather(*tasks)
    return JSONResponse({"message": "Fetch reading room data success"}, status_code=200)


async def fetch_reading_room_api(campus_name: str, campus_id: int) -> list[dict]:
    url = f"https://lib.hanyang.ac.kr/smufu-api/pc/{campus_id}/rooms-at-seat"

    reading_room_result = []
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response_json = await response.json()
            reading_room_list: list = response_json["data"]["list"]
            for reading_room_result_item in reading_room_list:
                reading_room_item = {
                    "name": reading_room_result_item["name"],
                    "isActive": reading_room_result_item["isActive"],
                    "isReservable": reading_room_result_item["isReservable"],
                    "total": reading_room_result_item["total"],
                    "activeTotal": reading_room_result_item["activeTotal"],
                    "occupied": reading_room_result_item["occupied"],
                    "available": reading_room_result_item["available"],
                }
                reading_room_result.append(reading_room_item)
    redis_connection = await get_redis_connection("reading_room")
    await set_redis_value(redis_connection, f"{campus_name}_reading_room",
                          json.dumps(reading_room_result, ensure_ascii=False).encode("utf-8"))
    await set_redis_value(redis_connection, f"{campus_name}_update_time",
                          datetime.now(tz=korea_standard_time).strftime("%m/%d/%Y, %H:%M:%S"))
    await redis_connection.close()
    return reading_room_result
