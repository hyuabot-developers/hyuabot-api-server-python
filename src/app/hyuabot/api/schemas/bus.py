from datetime import time
from pydantic import BaseModel, Field


class BusRealtimeItem(BaseModel):
    location: int
    remained_time: int = Field("remainedTime")
    remained_seat: int = Field("remainedSeat")


class BusRealtimeList(BaseModel):
    weekdays: list[time]
    saturday: list[time]
    sunday: list[time]


class BusDepartureByLine(BaseModel):
    line_name: str = Field(alias="lineName")  # 노선명
    realtime: list[BusRealtimeItem]  # 노선별 실시간 도착 정보
    timetable: BusRealtimeList  # 노선별 시간표 도착 정보


class BusStopInformationResponse(BaseModel):
    name: str = Field(alias="stopName")  # 정류장 이름
    departure_list: list[BusDepartureByLine] = Field(alias="departureInfoList")  # 노선별 도착 정보 목록
