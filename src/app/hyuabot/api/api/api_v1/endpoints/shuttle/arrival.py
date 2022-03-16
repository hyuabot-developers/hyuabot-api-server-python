import asyncio
import json
from datetime import datetime, timedelta
from typing import Tuple

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.hyuabot.api.api.api_v1.endpoints.shuttle import shuttle_stop_type
from app.hyuabot.api.core.database import get_redis_connection, get_redis_value
from app.hyuabot.api.core.date import get_shuttle_term, korea_standard_time
from app.hyuabot.api.schemas.shuttle import ShuttleDepartureByStop, ShuttleDepartureItem, \
    ShuttleDeparture

arrival_router = APIRouter(prefix="/arrival")
shuttle_stop_dict = {"Dormitory": "기숙사", "Shuttlecock_O": "셔틀콕", "Station": "한대앞",
                     "Terminal": "예술인A", "Shuttlecock_I": "셔틀콕 건너편"}


def compare_timetable(shuttle_time: datetime, now: datetime) -> bool:
    shuttle_time = shuttle_time.replace(year=now.year, month=now.month, day=now.day)
    return shuttle_time > now


async def fetch_timetable_by_stop(shuttle_stop: str, current_term: str,
                                  weekdays_keys: str, get_all: bool = False) -> \
        Tuple[list[ShuttleDepartureItem], list[ShuttleDepartureItem]]:
    now = datetime.now(tz=korea_standard_time)
    redis_connection = await get_redis_connection("shuttle")
    key = f"shuttle_{current_term}_{weekdays_keys}"
    json_string: bytes = await get_redis_value(redis_connection, key)
    timetable: list[dict] = json.loads(json_string.decode("utf-8"))

    shuttle_for_station: list[ShuttleDepartureItem] = []
    shuttle_for_terminal: list[ShuttleDepartureItem] = []

    for shuttle_index, shuttle_time in enumerate(timetable):
        shuttle_departure_time = datetime.strptime(shuttle_time["time"], "%H:%M")\
            .replace(tzinfo=korea_standard_time)
        shuttle_heading = shuttle_time["type"]
        if shuttle_stop == "Dormitory" and shuttle_time["startStop"] == "Dormitory":
            timedelta_minute = -5
            shuttle_departure_time += timedelta(minutes=timedelta_minute)
            if get_all or compare_timetable(shuttle_departure_time, now):
                if shuttle_heading == "DH":
                    shuttle_for_station.append(ShuttleDepartureItem(
                        time=shuttle_departure_time.strftime("%H:%M"), type=shuttle_time["type"],
                    ))
                elif shuttle_heading == "DY":
                    shuttle_for_terminal.append(ShuttleDepartureItem(
                        time=shuttle_departure_time.strftime("%H:%M"), type=shuttle_time["type"],
                    ))
                elif shuttle_heading == "C":
                    shuttle_for_station.append(ShuttleDepartureItem(
                        time=shuttle_departure_time.strftime("%H:%M"), type=shuttle_time["type"],
                    ))
                    shuttle_for_terminal.append(ShuttleDepartureItem(
                        time=shuttle_departure_time.strftime("%H:%M"), type=shuttle_time["type"],
                    ))
        elif shuttle_stop == "Shuttlecock_O":
            timedelta_minute = 0
            shuttle_departure_time += timedelta(minutes=timedelta_minute)
            if get_all or compare_timetable(shuttle_departure_time, now):
                if shuttle_heading == "DH":
                    shuttle_for_station.append(ShuttleDepartureItem(
                        time=shuttle_departure_time.strftime("%H:%M"), type=shuttle_time["type"],
                    ))
                elif shuttle_heading == "DY":
                    shuttle_for_terminal.append(ShuttleDepartureItem(
                        time=shuttle_departure_time.strftime("%H:%M"), type=shuttle_time["type"],
                    ))
                elif shuttle_heading == "C":
                    shuttle_for_station.append(ShuttleDepartureItem(
                        time=shuttle_departure_time.strftime("%H:%M"), type=shuttle_time["type"],
                    ))
                    shuttle_for_terminal.append(ShuttleDepartureItem(
                        time=shuttle_departure_time.strftime("%H:%M"), type=shuttle_time["type"],
                    ))
        elif shuttle_stop == "Station":
            timedelta_minute = 10
            shuttle_departure_time += timedelta(minutes=timedelta_minute)
            if get_all or compare_timetable(shuttle_departure_time, now):
                if shuttle_heading == "DH":
                    shuttle_for_station.append(ShuttleDepartureItem(
                        time=shuttle_departure_time.strftime("%H:%M"), type=shuttle_time["type"],
                    ))
                elif shuttle_heading == "C":
                    shuttle_for_station.append(ShuttleDepartureItem(
                        time=shuttle_departure_time.strftime("%H:%M"), type=shuttle_time["type"],
                    ))
                    shuttle_for_terminal.append(ShuttleDepartureItem(
                        time=shuttle_departure_time.strftime("%H:%M"), type=shuttle_time["type"],
                    ))
        elif shuttle_stop == "Terminal":
            if shuttle_heading == "DY":
                timedelta_minute = 10
                shuttle_departure_time += timedelta(minutes=timedelta_minute)
                if get_all or compare_timetable(shuttle_departure_time, now):
                    shuttle_for_terminal.append(ShuttleDepartureItem(
                        time=shuttle_departure_time.strftime("%H:%M"), type=shuttle_time["type"],
                    ))
            elif shuttle_heading == "C":
                timedelta_minute = 15
                shuttle_departure_time += timedelta(minutes=timedelta_minute)
                if get_all or compare_timetable(shuttle_departure_time, now):
                    shuttle_for_terminal.append(ShuttleDepartureItem(
                        time=shuttle_departure_time.strftime("%H:%M"), type=shuttle_time["type"],
                    ))
        elif shuttle_stop == "Shuttlecock_I" or shuttle_time["startStop"] == "Dormitory":
            if shuttle_heading == "DH" or shuttle_heading == "DY":
                timedelta_minute = 20
            else:
                timedelta_minute = 25
            shuttle_departure_time += timedelta(minutes=timedelta_minute)
            if get_all or compare_timetable(shuttle_departure_time, now):
                shuttle_for_terminal.append(ShuttleDepartureItem(
                        time=shuttle_departure_time.strftime("%H:%M"), type=shuttle_time["type"],
                ))
    await redis_connection.close()
    return shuttle_for_station, shuttle_for_terminal


@arrival_router.get("", status_code=200, response_model=ShuttleDeparture)
async def fetch_arrival_list():
    is_working, current_term, weekdays_keys = await get_shuttle_term()
    if not is_working:
        return JSONResponse(content={
            "message": "당일은 셔틀을 운행하지 않습니다.",
            "busForStation": [], "busForTerminal": [],
        })

    tasks = []
    for shuttle_stop in shuttle_stop_dict.keys():
        tasks.append(fetch_timetable_by_stop(shuttle_stop, current_term, weekdays_keys))

    results = []
    for shuttle_stop_name, (shuttle_for_station, shuttle_for_terminal) \
            in zip(shuttle_stop_dict.values(), await asyncio.gather(*tasks)):
        results.append(ShuttleDepartureByStop(
            stopName=shuttle_stop_name,
            busForStation=shuttle_for_station,
            busForTerminal=shuttle_for_terminal,
        ))
    return ShuttleDeparture(
        arrivalList=results,
    )


@arrival_router.get("/{shuttle_stop}", status_code=200, response_model=ShuttleDepartureByStop)
async def fetch_arrival_list_by_stop(shuttle_stop: str):
    if shuttle_stop not in shuttle_stop_type:
        return JSONResponse(status_code=404, content={"message": "존재하지 않는 셔틀버스 정류장입니다."})

    is_working, current_term, weekdays_keys = await get_shuttle_term()
    if not is_working:
        return JSONResponse(content={
            "message": "당일은 셔틀을 운행하지 않습니다.",
            "busForStation": [], "busForTerminal": [],
        })
    shuttle_for_station, shuttle_for_terminal = \
        await fetch_timetable_by_stop(shuttle_stop, current_term, weekdays_keys)
    return ShuttleDepartureByStop(
        stopName=shuttle_stop_dict[shuttle_stop],
        busForStation=shuttle_for_station,
        busForTerminal=shuttle_for_terminal,
    )


@arrival_router.get("/{shuttle_stop}/timetable", status_code=200, response_model=ShuttleDepartureByStop)
async def fetch_timetable_list_by_stop(shuttle_stop: str):
    if shuttle_stop not in shuttle_stop_type:
        return JSONResponse(status_code=404, content={"message": "존재하지 않는 셔틀버스 정류장입니다."})

    is_working, current_term, weekdays_keys = await get_shuttle_term()
    if not is_working:
        return JSONResponse(content={
            "message": "당일은 셔틀을 운행하지 않습니다.",
            "busForStation": [], "busForTerminal": [],
        })
    shuttle_for_station, shuttle_for_terminal = \
        await fetch_timetable_by_stop(shuttle_stop, current_term, weekdays_keys,  get_all=True)
    return ShuttleDepartureByStop(
        stopName=shuttle_stop_dict[shuttle_stop],
        busForStation=shuttle_for_station,
        busForTerminal=shuttle_for_terminal,
    )
