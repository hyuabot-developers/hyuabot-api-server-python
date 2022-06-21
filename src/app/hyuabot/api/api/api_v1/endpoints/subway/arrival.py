import asyncio
import datetime
import json

from fastapi import APIRouter, HTTPException

from app.hyuabot.api.core.date import get_shuttle_term, korea_standard_time
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

    timetable: list[dict] = []
    timetable_after = []

    for item in timetable:
        item_time = datetime.datetime.strptime(item["departureTime"], "%H:%M:%S").replace(
            year=now.year, month=now.month, day=now.day, tzinfo=korea_standard_time,
        )
        if item_time.hour < 4:
            item_time += datetime.timedelta(days=1)
        timetable_after.append(item)
    return timetable_after


async def fetch_subway_realtime_redis(line_id: str) -> tuple[str, dict]:
    return "", {}


@arrival_router.get("/{campus_name}", status_code=200, response_model=SubwayDepartureResponse)
async def fetch_subway_information(campus_name: str):
    subway_dict = {
        # "seoul": [("한양대", "1002")],
        "erica": [("한대앞", "1004"), ("한대앞", "1075")],
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
