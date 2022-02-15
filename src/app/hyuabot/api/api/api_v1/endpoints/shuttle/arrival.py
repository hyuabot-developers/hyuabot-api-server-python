import json
from datetime import datetime

import aioredis
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.hyuabot.api.api.api_v1.endpoints.shuttle import shuttle_stop_type
from app.hyuabot.api.core.config import settings
from app.hyuabot.api.core.date import get_shuttle_term
from app.hyuabot.api.schemas.shuttle import ShuttleDepartureByStop, ShuttleDepartureItem

arrival_router = APIRouter(prefix="/arrival")


@arrival_router.get("/station", status_code=200, response_model=ShuttleDepartureByStop)
async def fetch_arrival_list_by_stop(shuttle_stop: str):
    if shuttle_stop not in shuttle_stop_type:
        return JSONResponse(status_code=404, content={"message": "존재하지 않는 셔틀버스 정류장입니다."})

    is_working, current_term, weekdays_keys = await get_shuttle_term()
    if not is_working:
        return JSONResponse(content={
            "message": "당일은 셔틀을 운행하지 않습니다.",
            "busForStation": [], "busForTerminal": [],
        })

    now = datetime.now()
    redis_client = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}")
    async with redis_client.client() as connection:
        key = f"shuttle_{current_term}_{weekdays_keys}"
        json_string: bytes = await connection.get(key)
        timetable: list[dict] = json.loads(json_string.decode("utf-8"))

        shuttle_for_station: list[ShuttleDepartureItem] = []
        shuttle_for_terminal: list[ShuttleDepartureItem] = []

        for shuttle_index, shuttle_time in enumerate(timetable):
            shuttle_departure_time = datetime.strptime(shuttle_time["time"], "%H:%M").replace(
                year=now.year, month=now.month, day=now.day)
            if shuttle_departure_time < now:
                continue
            shuttle_type = shuttle_time["type"]
            shuttle_item = ShuttleDepartureItem(
                time=shuttle_time["time"], type=shuttle_time["type"],
            )
            if shuttle_type == "DH":
                shuttle_for_station.append(shuttle_item)
            elif shuttle_type == "DY":
                shuttle_for_terminal.append(shuttle_item)
            else:
                shuttle_for_station.append(shuttle_item)
                shuttle_for_terminal.append(shuttle_item)

    return JSONResponse(content=ShuttleDepartureByStop(
        message="정상 처리되었습니다.",
        busForStation=shuttle_for_station,
        busForTerminal=shuttle_for_terminal,
    ).dict())
