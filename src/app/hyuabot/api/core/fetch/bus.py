import asyncio
import json
from datetime import datetime

import aiohttp
from bs4 import BeautifulSoup
from fastapi import APIRouter
from starlette.responses import JSONResponse

from app.hyuabot.api.core.date import korea_standard_time

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
        tasks.append(fetch_bus_realtime(stop_id, line_id))
    await asyncio.gather(*tasks)
    return JSONResponse({"message": "Fetch bus data success"}, status_code=200)


async def fetch_bus_realtime(stop_id: str, route_id: str, bus_auth_key: str = None) -> list[dict]:
    if bus_auth_key is None:
        bus_auth_key = "1234567890"
        url = f'http://openapi.gbis.go.kr/ws/rest/busarrivalservice?' \
              f'serviceKey={bus_auth_key}&stationId={stop_id}&routeId={route_id}'
    else:
        url = f'http://apis.data.go.kr/6410000/busarrivalservice/getBusArrivalItem?' \
              f'serviceKey={bus_auth_key}&stationId={stop_id}&routeId={route_id}'
    timeout = aiohttp.ClientTimeout(total=3.0)
    arrival_list = []
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                soup = BeautifulSoup(await response.text(), "lxml")
                arrival_info_list = soup.find("response").find("msgbody")
                if arrival_info_list is not None:
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
    except asyncio.exceptions.TimeoutError:
        if bus_auth_key != "1234567890":
            arrival_list = await fetch_bus_realtime(stop_id, route_id, "1234567890")
        print("TimeoutError", url)
    except AttributeError:
        if bus_auth_key != "1234567890":
            arrival_list = await fetch_bus_realtime(stop_id, route_id, "1234567890")
        print("AttributeError", url)
    return arrival_list


async def fetch_bus_timetable_redis(route_id: str, day_key: str) -> list:
    timetable = []
    return timetable
