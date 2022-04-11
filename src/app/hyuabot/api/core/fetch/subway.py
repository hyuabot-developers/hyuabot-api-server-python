import asyncio
import json
from datetime import datetime

import aiohttp
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.hyuabot.api.core.config import AppSettings
from app.hyuabot.api.core.database import get_redis_connection, set_redis_value
from app.hyuabot.api.core.date import korea_standard_time

status_code_dict = {0: "진입", 1: "도착", 2: "출발", 3: "전역출발", 4: "전역진입", 5: "전역도착", 99: "운행중"}
minute_to_arrival = {
    "한대앞": 0, "중앙": 2, "고잔": 4, "초지": 6.5, "안산": 9, "신길온천": 12.5, "정왕": 16, "오이도": 19,
    "달월": 21, "월곶": 23, "소래포구": 25, "인천논현": 27, "호구포": 29, "남동인더스파크": 31, "원인재": 33,
    "연수": 35, "송도": 38.5, "인하대": 41, "숭의": 42.5, "신포": 45, "인천": 46.5,
    "상록수": 2, "반월": 6, "대야미": 8.5, "수리산": 11.5, "산본": 13.5, "금정": 18,
    "범계": 21.5, "평촌": 23.5, "인덕원": 26, "정부과천청사": 28, "과천": 30,
    "사리": 2, "야목": 7, "어천": 10, "오목천": 14, "고색": 17, "수원": 21, "매교": 23, "수원시청": 26,
    "매탄권선": 29, "망포": 31.5, "영통": 34, "청명": 36, "상갈": 39, "기흥": 41.5, "신갈": 44, "구성": 46.5,
    "보정": 49, "죽전": 52, "오리": 55.5, "미금": 57.5, "정지": 60, "수내": 62.5, "서현": 64.5, "이매": 66.5
}
fetch_subway_router = APIRouter(prefix="/subway")


@fetch_subway_router.get("", status_code=200)
async def fetch_subway_realtime_information() -> JSONResponse:
    tasks = [
        get_subway_realtime_information("한양대"), get_subway_realtime_information("한대앞"),
    ]
    await asyncio.gather(*tasks)
    return JSONResponse({"message": "Fetch subway data success"}, status_code=200)


async def get_subway_realtime_information(station_name: str) -> dict:
    app_settings = AppSettings()
    url = f"http://swopenapi.seoul.go.kr/api/subway/{app_settings.METRO_API_KEY}/json/" \
          f"realtimeStationArrival/0/10/{station_name}"
    timeout = aiohttp.ClientTimeout(total=3.0)
    arrival_list: dict[str, dict] = {}
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url) as response:
            response_json = await response.json()
            if "realtimeArrivalList" in response_json.keys():
                realtime_arrival_list = response_json["realtimeArrivalList"]
                for realtime_arrival_item in realtime_arrival_list:
                    line_id = realtime_arrival_item["subwayId"]
                    up_down = realtime_arrival_item["updnLine"]
                    terminal_station = realtime_arrival_item["bstatnNm"]
                    current_station = realtime_arrival_item["arvlMsg3"]
                    status_code = realtime_arrival_item["arvlCd"]

                    if line_id not in arrival_list.keys():
                        arrival_list[line_id] = {"up": [], "down": []}
                    if up_down == "상행" or up_down == "내선":
                        up_down_key = "up"
                    elif up_down == "하행" or up_down == "외선":
                        up_down_key = "down"
                    if current_station in minute_to_arrival.keys():
                        remained_time = minute_to_arrival[current_station]
                    else:
                        remained_time = 0
                    arrival_list[line_id][up_down_key].append({
                        "terminalStation": terminal_station,
                        "currentStation": current_station,
                        "remaiedTime": remained_time,
                        "statusCode": status_code_dict[int(status_code)],
                    })

                redis_connection = await get_redis_connection("subway")
                for line_id in arrival_list.keys():
                    await set_redis_value(redis_connection, f"subway_{station_name}_{line_id}_arrival",
                                          json.dumps(
                                              arrival_list[line_id], ensure_ascii=False).encode("utf-8"))
                    await set_redis_value(redis_connection,
                                          f"subway_{station_name}_{line_id}_update_time",
                                          datetime.now(tz=korea_standard_time)
                                          .strftime("%m/%d/%Y, %H:%M:%S"))
                await redis_connection.close()
    return arrival_list
