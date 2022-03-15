import asyncio
import json
from datetime import datetime

import aiohttp
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.hyuabot.api.core.config import AppSettings
from app.hyuabot.api.core.database import get_redis_connection, set_redis_value

status_code_dict = {0: "진입", 1: "도착", 2: "출발", 3: "전역출발", 4: "전역진입", 5: "전역도착", 99: "운행중"}
fetch_subway_router = APIRouter(prefix="/subway")


@fetch_subway_router.get("", status_code=200)
async def fetch_subway_realtime_information() -> JSONResponse:
    tasks = [
        get_subway_realtime_information("한양대"), get_subway_realtime_information("한대앞")
    ]
    await asyncio.gather(*tasks)
    return JSONResponse({"message": "Fetch subway data success"}, status_code=200)


async def get_subway_realtime_information(station_name: str) -> dict:
    app_settings = AppSettings()
    url = f"http://swopenapi.seoul.go.kr/api/subway/{app_settings.METRO_API_KEY}/json/" \
          f"realtimeStationArrival/0/10/{station_name}"
    timeout = aiohttp.ClientTimeout(total=3.0)
    arrival_list = {}
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url) as response:
            response_json = await response.json()
            realtime_arrival_list = response_json["realtimeArrivalList"]
            for realtime_arrival_item in realtime_arrival_list:
                line_id = realtime_arrival_item["subwayId"]
                up_down = realtime_arrival_item["updnLine"]
                terminal_station = realtime_arrival_item["bstatnNm"]
                current_station = realtime_arrival_item["arvlMsg3"]
                status_code = realtime_arrival_item["arvlCd"]

                if line_id not in arrival_list.keys():
                    arrival_list[line_id] = {"up": [], "down": []}
                if up_down == "상행" or up_down == "내선":
                    up_down_key = "up"
                elif up_down == "하행" or up_down == "외선":
                    up_down_key = "down"
                arrival_list[line_id][up_down_key].append({
                    "terminalStation": terminal_station,
                    "currentStation": current_station,
                    "statusCode": status_code_dict[int(status_code)]
                })

            redis_connection = await get_redis_connection("subway")
            for line_id in arrival_list.keys():
                await set_redis_value(redis_connection, f"subway_{station_name}_{line_id}_arrival",
                                      json.dumps(
                                          arrival_list[line_id], ensure_ascii=False).encode("utf-8"))
                await set_redis_value(redis_connection, f"subway_{station_name}_{line_id}_update_time",
                                      datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
            await redis_connection.close()
    return arrival_list
