from datetime import time
from enum import Enum
from pydantic import BaseModel, HttpUrl, Field


class ShuttleType(Enum):
    DH = 1  # 한대앞 직행
    DY = 2  # 예술인 직행
    C = 3  # 순환 버스


class ShuttleDepartureItem(BaseModel):
    time: time
    type: ShuttleType


class ShuttleDepartureByStop(BaseModel):
    for_station: str = Field(alias="busForStation")
    for_terminal: str = Field(alias="busForTerminal")


class ShuttleStopResponse(BaseModel):
    road_view: HttpUrl = Field(alias="roadViewLink")
    first_bus_station: time = Field(alias="firstBusForStation")
    last_bus_station: time = Field(alias="lastBusForStation")
    first_bus_terminal: time = Field(alias="firstBusForTerminal")
    last_bus_terminal: time = Field(alias="lastBusForTerminal")
    weekdays: ShuttleDepartureByStop
    weekends: ShuttleDepartureByStop
