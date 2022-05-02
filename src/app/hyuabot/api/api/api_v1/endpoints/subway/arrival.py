import asyncio
import datetime
import json

from fastapi import APIRouter, HTTPException

from app.hyuabot.api.core.database import get_redis_connection, get_redis_value
from app.hyuabot.api.core.date import get_shuttle_term, korea_standard_time
from app.hyuabot.api.core.fetch.subway import get_subway_realtime_information
from app.hyuabot.api.schemas.subway import \
    SubwayDepartureResponse, SubwayDepartureByLine, SubwayTimetableList

arrival_router = APIRouter(prefix="/arrival")


async def fetch_subway_timetable(line_id: str) -> dict:
    _, _, weekday_key, _ = await get_shuttle_term()

    tasks = [
        fetch_subway_timetable_redis(line_id, weekday_key, "up"),
        fetch_subway_timetable_redis(line_id, weekday_key, "down"),
    ]
    [timetable_up, timetable_down] = await asyncio.gather(*tasks)
    return {"up": timetable_up, "down": timetable_down}


async def fetch_subway_timetable_redis(line_id: str, day: str, heading: str) -> list[dict]:
    now = datetime.datetime.now(tz=korea_standard_time)

    redis_connection = await get_redis_connection("subway")
    json_string = await get_redis_value(redis_connection, f"subway_{line_id}_{day}_{heading}")
    timetable: list[dict] = json.loads(json_string.decode("utf-8"))
    timetable_after = []

    for item in timetable:
        item_time = datetime.datetime.strptime(item["departureTime"], "%H:%M:%S").replace(
            year=now.year, month=now.month, day=now.day, tzinfo=korea_standard_time,
        )
        if item_time.hour < 4:
            item_time += datetime.timedelta(days=1)
        if item_time < now:
            continue
        timetable_after.append(item)
    await redis_connection.close()
    return timetable_after


async def fetch_subway_realtime_redis(line_id: str) -> tuple[str, dict]:
    redis_connection = await get_redis_connection("subway")
    arrival_list_string = \
        await get_redis_value(redis_connection, f"subway_{line_id}_position")

    arrival_list = json.loads(arrival_list_string.decode("utf-8"))
    await redis_connection.close()
    return arrival_list


@arrival_router.get("/{campus_name}", status_code=200, response_model=SubwayDepartureResponse)
async def fetch_subway_information(campus_name: str):
    subway_dict = {
        "seoul": [("한양대", "1002")], "erica": [("한대앞", "1004"), ("한대앞", "1075")],
    }

    if campus_name not in subway_dict:
        raise HTTPException(status_code=404, detail="Campus name is invalid")

    tasks = []
    for station_name, line_id in subway_dict[campus_name]:
        tasks.append(fetch_subway_realtime_redis(line_id))

    if campus_name == "seoul":
        main_line_arrival = await asyncio.gather(*tasks)
        return SubwayDepartureResponse(
            stationName=subway_dict[campus_name][0][0],
            departureList=[
                SubwayDepartureByLine(
                    lineName="2호선",
                    realtime=main_line_arrival,
                    timetable=SubwayTimetableList(up=[], down=[]),
                ),
            ],
        )
    [main_line_arrival, sub_line_arrival] = await asyncio.gather(*tasks)
    return SubwayDepartureResponse(
        stationName=subway_dict[campus_name][0][0],
        departureList=[
            SubwayDepartureByLine(
                lineName="4호선",
                realtime=main_line_arrival,
                timetable=await fetch_subway_timetable("1004"),
            ),
            SubwayDepartureByLine(
                lineName="수인분당선",
                realtime=sub_line_arrival,
                timetable=await fetch_subway_timetable("1075"),
            ),
        ],
    )
