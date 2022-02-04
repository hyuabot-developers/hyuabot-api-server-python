from datetime import time
from pydantic.main import BaseModel


class BusRealtimeItem(BaseModel):
    location: int
    remainedTime: int
    remainedSeat: int


class BusRealtimeList(BaseModel):
    weekdays: list[time]
    saturday: list[time]
    sunday: list[time]


class BusDepartureByLine(BaseModel):
    lineName: str  # 노선명
    realtime: list[BusRealtimeItem]  # 노선별 실시간 도착 정보
    timetable: BusRealtimeList  # 노선별 시간표 도착 정보


class BusStopInformation(BaseModel):
    stopName: str  # 정류장 이름
    departureInfoList: list[BusDepartureByLine]  # 노선별 도착 정보 목록
