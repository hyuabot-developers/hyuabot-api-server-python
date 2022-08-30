import asyncio

import aiohttp
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.hyuabot.api.core.config import AppSettings
from app.hyuabot.api.models.postgresql.subway import SubwayRealtime
from app.hyuabot.api.utlis.fastapi import get_db_session

status_code_dict = {0: "진입", 1: "도착"}
line_code_dict = {"2호선": 1002, "4호선": 1004, "수인분당선": 1075}
minute_to_arrival = {'당고개': 95.5, '상계': 93.5, '노원': 91.5,
                     '창동': 89.5, '쌍문': 87.0, '수유': 84.5, '미아': 82.5,
                     '미아사거리': 80.0, '길음': 77.5, '성신여대입구': 75.0, '한성대입구': 73.0, '혜화': 71.0,
                     '동대문': 68.5, '동대문역사문화공원': 67.0, '충무로': 64.5, '명동': 63.0, '회현': 61.5,
                     '서울': 59.5, '숙대입구': 57.5, '삼각지': 55.5, '신용산': 54.0, '이촌': 51.5,
                     '동작': 48.0, '총신대입구(이수)': 45.0, '사당': 43.0, '남태령': 40.5, '선바위': 37.5,
                     '경마공원': 35.5, '대공원': 33.5, '과천': 31.5, '정부과천청사': 29.5, '인덕원': 26.0,
                     '평촌': 23.5, '범계': 21.5, '금정': 18.0, '산본': 13.5, '수리산': 11.5, '대야미': 8.0,
                     '반월': 5.5, '상록수': 2.0, '한대앞': 0.0, '중앙': 2.5, '고잔': 4.5, '초지': 7.0,
                     '안산': 9.5, '신길온천': 13.0, '정왕': 16.0, '오이도': 19.0, '신포': 47.0, '숭의': 44.5,
                     '인하대': 42.0, '송도': 39.5, '연수': 36.0, '원인재': 34.0, '남동인더스파크': 32.0,
                     '호구포': 30.0, '인천논현': 28.0, '소래포구': 26.0, '월곶': 24.0, '달월': 21.5,
                     '사리': 3.5, '야목': 8.5, '어천': 11.5, '오목천': 16.0, '고색': 18.5, '수원': 22.5,
                     '매교': 25.0, '수원시청': 27.5, '매탄권선': 30.5, '망포': 33.0, '영통': 35.5,
                     '청명': 37.5, '상갈': 41.0, '기흥': 43.5, '신갈': 46.0, '구성': 48.5, '보정': 51.0,
                     '죽전': 54.0, '오리': 57.5, '미금': 59.5, '정자': 62.0, '수내': 64.5, '서현': 66.5,
                     '이매': 68.5, '야탑': 71.0, '모란': 74.0, '태평': 76.0, '가천대': 78.0, '복정': 81.0,
                     '수서': 85.0, '대모산입구': 89.0, '개포동': 90.5, '구룡': 92.5, '도곡': 94.0,
                     '한티': 95.5, '선릉': 97.5, '선정릉': 99.5, '강남구청': 101.0, '로데오': 103.5,
                     '서울숲': 105.5, '왕십리': 109.0, '청량리': 118.0}
fetch_subway_router = APIRouter(prefix="/subway")


@fetch_subway_router.get("", status_code=200)
async def fetch_subway_realtime_information(db_session: Session = Depends(get_db_session)) \
        -> JSONResponse:
    db_session.query(SubwayRealtime).delete()
    tasks = [
        # get_subway_realtime_information("2호선"),
        get_subway_realtime_information(db_session, "4호선", "한대앞"),
        get_subway_realtime_information(db_session, "수인분당선", "한대앞"),
    ]
    await asyncio.gather(*tasks)
    db_session.commit()
    return JSONResponse({"message": "Fetch subway data success"}, status_code=200)


async def get_subway_realtime_information(db_session: Session, route_name: str, station_name: str) \
        -> None:
    app_settings = AppSettings()
    count = 5 if app_settings.METRO_API_KEY == "sample" else 60
    url = f"http://swopenapi.seoul.go.kr/api/subway/{app_settings.METRO_API_KEY}/json/" \
          f"realtimePosition/0/{count}/{route_name}"
    timeout = aiohttp.ClientTimeout(total=3.0)
    arrival_list: list[SubwayRealtime] = []
    train_number_list: list[str] = []
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url) as response:
            response_json = await response.json()
            if "realtimePositionList" in response_json.keys():
                realtime_position_list = response_json["realtimePositionList"]
                for realtime_position_item in realtime_position_list:
                    current_station = realtime_position_item["statnNm"]
                    train_number = realtime_position_item["trainNo"]
                    update_time = realtime_position_item["recptnDt"]
                    heading = realtime_position_item["updnLine"]
                    terminal_station = realtime_position_item["statnTnm"]
                    status_code = realtime_position_item["trainSttus"]
                    is_express_train = realtime_position_item["directAt"]
                    is_last_train = realtime_position_item["lstcarAt"]
                    if route_name == "2호선":
                        pass
                    elif route_name == "4호선":
                        if is_express_train == "1":
                            continue
                        elif heading == "0" and \
                                (terminal_station not in ["당고개", "노원", "한성대입구"] or
                                 current_station not in list(minute_to_arrival.keys())[41:48]):
                            continue
                        elif heading == "1" and \
                                (terminal_station not in ["오이도", "안산"] or
                                 current_station not in list(minute_to_arrival.keys())[:40]):
                            continue
                    elif route_name == "수인분당선":
                        if is_express_train == "1":
                            continue
                        elif heading == "0" and \
                                (terminal_station not in ["왕십리", "죽전", "고색"] or
                                 current_station not in list(minute_to_arrival.keys())[41:60]):
                            continue
                        elif heading == "1" and \
                                (terminal_station not in ["오이도", "인천"] or
                                 current_station not in list(minute_to_arrival.keys())[60:]):
                            continue
                    if train_number in train_number_list:
                        arrival_list.remove(arrival_list[train_number_list.index(train_number)])
                        train_number_list.remove(train_number)
                    train_number_list.append(train_number)
                    subway_item = SubwayRealtime(
                        route_name=route_name,
                        station_name=station_name,
                        heading=heading.replace("0", "up").replace("1", "down"),
                        update_time=update_time,
                        train_number=train_number,
                        last_train=bool(int(is_last_train)),
                        terminal_station=terminal_station,
                        current_station=current_station,
                        remained_time=minute_to_arrival[current_station]
                        if current_station in minute_to_arrival.keys() else 0,
                        status=status_code_dict[int(status_code)]
                        if int(status_code) in status_code_dict.keys() else "출발",
                    )
                    arrival_list.append(subway_item)
    db_session.add_all(arrival_list)
