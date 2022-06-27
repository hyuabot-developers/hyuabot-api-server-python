from datetime import time

from fastapi import Query

from app.hyuabot.api.models.postgresql import bus as db
from app.hyuabot.api.schemas.bus import BusRealtimeItem

bus_route_dict = {
    "10-1": ("216000068", "216000379"),
    "707-1": ("216000070", "216000719"),
    "3102": ("216000061", "216000379"),
}
bus_stop_dict = {
    "216000379": "한양대컨벤션센터",
    "216000719": "한양대정문",
}

timetable_limit = Query(None, alias="count", description="버스 시간표를 얼마나 반환할지", example="2")


def convert_bus_realtime_item(items: list[db.BusRealtime]) -> list[BusRealtimeItem]:
    return [
        BusRealtimeItem(
            low_plate=item.low_plate,
            location=item.remained_stop,
            remained_time=item.remained_time,
            remained_seat=item.remained_seat,
        )
        for item in items
    ]


def convert_bus_timetable_item(items: list[db.BusTimetable]) -> list[time]:
    return [item.departure_time for item in items]
