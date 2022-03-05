import asyncio
import json
from datetime import datetime

import aiohttp
from bs4 import BeautifulSoup
from fastapi import APIRouter
from starlette.responses import JSONResponse

from app.hyuabot.api.core.config import AppSettings
from app.hyuabot.api.core.database import get_redis_connection, get_redis_value, set_redis_value

fetch_bus_router = APIRouter(prefix="/bus")


@fetch_bus_router.get("", status_code=200)
async def fetch_bus_realtime_in_a_row() -> JSONResponse:
    bus_route_dict = {
        "10-1": ("216000068", "216000379"),
        "707-1": ("216000070", "216000719"),
        "3102": ("216000061", "216000379"),
    }

    tasks = []
    for line_name, (line_id, stop_id) in bus_route_dict.items():
        tasks.append(fetch_bus_realtime(line_id, stop_id))
    await asyncio.gather(*tasks)
    return JSONResponse({"message": "Fetch bus data success"}, status_code=200)


async def fetch_bus_realtime(stop_id: str, route_id: str) -> list[dict]:
    bus_auth_key: str = AppSettings().BUS_API_KEY
    url = "http://openapi.gbis.go.kr/ws/rest/busarrivalservice"
    params = {"serviceKey": bus_auth_key, "stationId": stop_id, "routeId": route_id}

    timeout = aiohttp.ClientTimeout(total=3.0)
    arrival_list = []
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url, params=params) as response:
            soup = BeautifulSoup(await response.text(), "lxml")
            arrival_info_list = soup.find("response").find("msgbody")
            if arrival_info_list is None:
                return []
            arrival_info_list = arrival_info_list.find("busarrivalitem")
            location, low_plate, predict_time, remained_seat = \
                arrival_info_list.find("locationno1").text, \
                arrival_info_list.find("lowplate1").text, \
                arrival_info_list.find("predicttime1").text, \
                arrival_info_list.find("remainseatcnt1").text
            arrival_list.append({
                "location": location,
                "lowPlate": low_plate,
                "remainedTime": predict_time,
                "remainedSeat": remained_seat,
            })

            if arrival_info_list.find("locationno2") and \
                    arrival_info_list.find("locationno2").text and \
                    arrival_info_list.find("predicttime2").text:
                location, low_plate, predict_time, remained_seat = \
                    arrival_info_list.find("locationno2").text, \
                    arrival_info_list.find("lowplate2").text, \
                    arrival_info_list.find("predicttime2").text, \
                    arrival_info_list.find("remainseatcnt2").text
                arrival_list.append({
                    "location": location,
                    "lowPlate": low_plate,
                    "remainedTime": predict_time,
                    "remainedSeat": remained_seat,
                })
            redis_connection = await get_redis_connection("bus")
            await set_redis_value(redis_connection, f"{stop_id}_{route_id}_arrival",
                                  json.dumps(arrival_list, ensure_ascii=False).encode("utf-8"))
            await set_redis_value(redis_connection, f"{stop_id}_{route_id}_update_time",
                                  datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
            await redis_connection.close()

            return arrival_list


async def fetch_bus_timetable_redis(route_id: str, day_key: str) -> list:
    redis_connection = await get_redis_connection("bus")

    key = f"bus_{route_id}_{day_key}"
    json_string: bytes = await get_redis_value(redis_connection, key)
    timetable: list[str] = json.loads(json_string.decode("utf-8"))
    await redis_connection.close()
    return timetable
