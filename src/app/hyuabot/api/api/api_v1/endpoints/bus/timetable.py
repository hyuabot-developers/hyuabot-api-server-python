import asyncio

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.hyuabot.api.api.api_v1.endpoints.bus import bus_route_query, bus_route_dict
from app.hyuabot.api.core.fetch.bus import fetch_bus_timetable_redis
from app.hyuabot.api.schemas.bus import BusTimetable

timetable_router = APIRouter(prefix="/timetable")


@timetable_router.get("", status_code=200, response_model=BusTimetable)
async def fetch_bus_timetable(bus_line_id: str = bus_route_query):
    if bus_line_id not in bus_route_dict.keys():
        return JSONResponse(status_code=404, content={"message": "제공되지 않는 버스 노선입니다."})

    day_keys = ["weekdays", "saturday", "sunday"]
    weekdays_timetable, saturday_timetable, sunday_timetable = await asyncio.gather(
        fetch_bus_timetable_redis(bus_line_id, day_keys[0]),
        fetch_bus_timetable_redis(bus_line_id, day_keys[1]),
        fetch_bus_timetable_redis(bus_line_id, day_keys[2]),
    )
    timetable = BusTimetable(weekdays=weekdays_timetable,
                             saturday=saturday_timetable,
                             sunday=sunday_timetable)
    return timetable
