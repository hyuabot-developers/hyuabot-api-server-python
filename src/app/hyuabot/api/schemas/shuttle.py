from datetime import time
from enum import Enum
from pydantic import BaseModel, HttpUrl, Field


class ShuttleType(Enum):
    DH = 1  # 한대앞 직행
    DY = 2  # 예술인 직행
    C = 3  # 순환 버스


class ShuttleDepartureItem(BaseModel):
    time: str = Field(alias="time", title="정류장 출발 시간", description="예시: '09:00'")
    type: str = Field(alias="type", title="셔틀 행선지", description="예시: 'DH'")


class ShuttleDepartureByStop(BaseModel):
    for_station: list[ShuttleDepartureItem] = Field(alias="busForStation", title="한대앞 방면 출발 시간",
                                                    description="예시: [{'time': '09:00', 'type': 'DH'}]")
    for_terminal: list[ShuttleDepartureItem] = Field(alias="busForTerminal", title="예술인 방면 출발 시간",
                                                     description="예시: [{'time': '09:00', 'type': 'DY'}]")


class ShuttleStopResponse(BaseModel):
    road_view: HttpUrl = Field(alias="roadViewLink", title="로드뷰 링크",
                               description="예시: 'https://www.hyuabot.com/roadview/'")
    first_bus_station: time = Field(alias="firstBusForStation",
                                    title="한대앞 방면 첫차 시간", description="예시: '09:00'")
    last_bus_station: time = Field(alias="lastBusForStation",
                                   title="한대앞 방면 막차 시간", description="예시: '22:00'")
    first_bus_terminal: time = Field(alias="firstBusForTerminal",
                                     title="예술인 방면 첫차 시간", description="예시: '09:00'")
    last_bus_terminal: time = Field(alias="lastBusForTerminal",
                                    title="예술인 방면 막차 시간", description="예시: '22:00'")
    weekdays: ShuttleDepartureByStop = Field(alias="weekdays", title="주중 셔틀 출발 시간")
    weekends: ShuttleDepartureByStop = Field(alias="weekends", title="주말 셔틀 출발 시간")


# 셔틀 정류장 정보
class ShuttleStop(BaseModel):
    name_korean: str = Field(alias="koreanName", title="셔틀 정류장 이름(국문)",
                             description="예시: '셔틀콕'")
    name_english: str = Field(alias="englishName", title="셔틀 정류장 이름(영문)",
                              description="예시: 'Shuttlecock'")
    longitude: float = Field(alias="longitude", title="셔틀 정류장 경도", description="예시: '127.0'")
    latitude: float = Field(alias="latitude", title="셔틀 정류장 위도", description="예시: '37.5'")


# 셔틀 정류장 목록
class ShuttleRouteStationListResponse(BaseModel):
    message: str = Field(alias="message", title="메시지")
    station_list: list[ShuttleStop] = Field(alias="stationList", title="셔틀 정류장 목록")


# 노선별 셔틀버스
class ShuttleListItem(BaseModel):
    current_station: str = Field(alias="currentStation", title="현재 정류장")
    current_station_seq: int = Field(alias="currentStationSeq", title="현재 정류장 순서")
    last_shuttle: bool = Field(alias="lastShuttle", title="막차 여부")


# 노선별 셔틀버스 목록
class ShuttleListResponse(BaseModel):
    message: str = Field(alias="message", title="메시지")
    shuttle_list: list[ShuttleListItem] = Field(alias="shuttleList", title="셔틀 목록")
