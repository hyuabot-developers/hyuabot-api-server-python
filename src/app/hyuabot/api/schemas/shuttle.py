from datetime import time
from enum import Enum
from pydantic import BaseModel, HttpUrl


class ShuttleType(Enum):
    DH: 1  # 한대앞 직행
    DY: 2  # 예술인 직행
    C: 3  # 순환 버스


class ShuttleDepartureItem(BaseModel):
    time: time
    type: ShuttleType


class ShuttleDepartureByStop(BaseModel):
    busForStation: str
    busForTerminal: str


class ShuttleStopInformation(BaseModel):
    roadViewLink: HttpUrl
    firstBusForStation: time
    lastBusForStation: time
    firstBusForTerminal: time
    lastBusForTerminal: time
    weekdays: ShuttleDepartureByStop
    weekends: ShuttleDepartureByStop
