# Query params
from fastapi import Query

bus_route_dict = {
    "10-1": ("216000068", "216000379"),
    "707-1": ("216000070", "216000719"),
    "3102": ("216000061", "216000379"),
}
bus_stop_dict = {
    "216000379": "한양대컨벤션센터",
    "216000719": "한양대정문",
}
bus_route_query = Query(None, alias="busLineID", description="버스 노선(10-1, 707-1, 3102)",
                           regex="^(10-1|707-1|3102)$", example="3102")
bus_stop_query = Query("216000379", alias="busStopID", description="정류장 ID(216000379)",
                       regex="^[0-9]{9}$", example="216000379")
timetable_limit = Query(None, alias="count", description="버스 시간표를 얼마나 반환할지", example="2")
