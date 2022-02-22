import asyncio
import datetime
import json

import aioredis

from app.hyuabot.api.core.config import settings
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.hyuabot.api.api.api_v1.endpoints.bus import bus_route_query, bus_route_dict, bus_stop_query, \
    timetable_limit
from app.hyuabot.api.api.fetch.bus import fetch_bus_timetable_redis, fetch_bus_realtime
from app.hyuabot.api.schemas.bus import BusDepartureByLine, BusTimetable

arrival_router = APIRouter(prefix="/arrival")


@arrival_router.get("", status_code=200, response_model=BusDepartureByLine)
async def fetch_bus_information_by_route(bus_line_id: str = bus_route_query,
                                         bus_stop_id: str = bus_stop_query,
                                         timetable_count: int | None = timetable_limit):
    if bus_line_id not in bus_route_dict.keys():
        return JSONResponse(status_code=404, content={"message": "제공되지 않는 버스 노선입니다."})

    now = datetime.datetime.now()
    redis_client = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}")
    async with redis_client.client() as connection:
        update_time, arrival_list_string = await connection.mget(
            f"{bus_stop_id}_{bus_route_dict[bus_line_id]}_update_time",
            f"{bus_stop_id}_{bus_route_dict[bus_line_id]}_arrival",
        )

        if update_time is not None:
            updated_before = (now - datetime.datetime.strptime(
                update_time.decode("utf-8"), "%m/%d/%Y, %H:%M:%S")
            ).seconds
        if updated_before < 60:
            arrival_list: list[dict] = json.loads(arrival_list_string.decode("utf-8"))
        else:
            arrival_list: list[dict] = await fetch_bus_realtime(bus_stop_id, bus_route_dict[bus_line_id])

    day_keys = ["weekdays", "saturday", "sunday"]
    weekdays_timetable, saturday_timetable, sunday_timetable = await asyncio.gather(
        fetch_bus_timetable_redis(bus_line_id, day_keys[0]),
        fetch_bus_timetable_redis(bus_line_id, day_keys[1]),
        fetch_bus_timetable_redis(bus_line_id, day_keys[2]),
    )
    message = "정상 처리되었습니다."
    timetable = BusTimetable(weekdays=weekdays_timetable[:timetable_count
                                if timetable_count else len(weekdays_timetable)],
                             saturday=saturday_timetable[:timetable_count
                                if timetable_count else len(saturday_timetable)],
                             sunday=sunday_timetable[:timetable_count
                                if timetable_count else len(sunday_timetable)])
    return BusDepartureByLine(message=message, name=bus_line_id, busStop=bus_stop_id,
                              realtime=arrival_list, timetable=timetable)
