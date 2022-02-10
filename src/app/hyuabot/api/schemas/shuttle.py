from datetime import time
from enum import Enum
from pydantic import BaseModel, HttpUrl, Field


class ShuttleType(Enum):
    DH = 1  # 한대앞 직행
    DY = 2  # 예술인 직행
    C = 3  # 순환 버스


class ShuttleDepartureItem(BaseModel):
    time: time = Field(alias="time", title="정류장 출발 시간", description="예시: '09:00'")
    type: ShuttleType = Field(alias="type", title="셔틀 행선지", description="예시: 'DH'")


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
