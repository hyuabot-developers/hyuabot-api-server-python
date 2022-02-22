import asyncio
import json
from datetime import datetime

import aiohttp
import aioredis

from app.hyuabot.api.api.fetch import fetch_router
from app.hyuabot.api.schemas.bus import BusRealtimeItem
from lxml import etree
from starlette.responses import JSONResponse

from app.hyuabot.api.core.config import settings


async def fetch_bus_timetable_redis(route_id: str, day_key: str) -> list:
    redis_client = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}")

    async with redis_client.client() as connection:
        key = f"bus_{route_id}_{day_key}"
        json_string: bytes = await connection.get(key)
        timetable: list[str] = json.loads(json_string.decode("utf-8"))
        return timetable


@fetch_router.get("/bus", status_code=200)
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
    return JSONResponse({"error": "Fetch bus data success"}, status_code=200)


async def fetch_bus_realtime(stop_id: str, route_id: str) -> list:
    bus_auth_key = settings.BUS_AUTH_KEY
    url = "http://openapi.gbis.go.kr/ws/rest/busarrivalservice"
    params = {"serviceKey": bus_auth_key, "stationId": stop_id, "routeId": route_id}

    timeout = aiohttp.ClientTimeout(total=3.0)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url, params=params) as response:
            response_xml = etree.fromstring((await response.text()).encode("utf-8"))

            xml_body = response_xml.find("msgBody")
            if xml_body is None:
                return []
            message_body = xml_body[0]
            arrival_list = []
            location_1 = message_body.find("locationNo1")
            if len(location_1) > 0:
                low_plate_1 = message_body.find("lowPlate1")
                predict_time_1 = message_body.find("predictTime1")
                remained_seat_1 = message_body.find("remainSeatCnt1")
                arrival_list.append(
                    BusRealtimeItem(
                        location_1.text,
                        low_plate_1.text,
                        predict_time_1.text,
                        remained_seat_1.text,
                    ).dict()
                )
                location_2 = message_body.find("locationNo2")
                if len(location_2) > 0:
                    low_plate_2 = message_body.find("lowPlate2")
                    predict_time_2 = message_body.find("predictTime2")
                    remained_seat_2 = message_body.find("remainSeatCnt2")
                    arrival_list.append(
                        BusRealtimeItem(
                            location_2.text,
                            low_plate_2.text,
                            predict_time_2.text,
                            remained_seat_2.text,
                        ).dict()
                    )
            redis_client = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}")
            async with redis_client.client() as connection:
                await connection.set(f"{stop_id}_{route_id}_arrival",
                               json.dumps(arrival_list, ensure_ascii=False).encode("utf-8"))
                await connection.set(f"{stop_id}_{route_id}_update_time",
                                     datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
                return arrival_list
