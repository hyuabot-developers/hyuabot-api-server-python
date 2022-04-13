from datetime import time
from pydantic import BaseModel, Field


class BusRealtimeItem(BaseModel):
    location: int = Field(alias="location", title="잔여 정류장 수", description="예시: 1 -> 정류장 1개 남음")
    low_plate: int = Field(alias="lowPlate", title="저상버스 여부", description="저상버스: 1/ 일반: 0")
    remained_time: int = Field(alias="remainedTime", title="남은 시간", description="예시: 10 -> 10분 남음")
    remained_seat: int = Field(alias="remainedSeat", title="잔여 좌석 수",
                               description="예시: 1 -> 좌석 1개 남음/예시: 0 -> 좌석 없음/예시: -1 -> 좌석 정보 미제공")


class BusTimetable(BaseModel):
    weekdays: list[time] = Field(alias="weekdays", title="평일 시점 출발 시간표")
    saturday: list[time] = Field(alias="saturday", title="토요일 시점 출발 시간표")
    sunday: list[time] = Field(alias="sunday", title="일요일/공휴일 시점 출발 시간표")


class BusDepartureByLine(BaseModel):
    message: str = Field(alias="message", title="메시지")
    name: str = Field(alias="name", title="노선명", description="예시: 3102")
    start_stop: str = Field(alias="startStop", title="출발정류장", description="예시: 서울역")
    terminal_stop: str = Field(alias="terminalStop", title="종점정류장", description="예시: 신림역")
    time_from_start_stop: str = Field(alias="timeFromStartStop", title="출발정류장으로부터 시간")
    bus_stop: str = Field(alias="busStop", title="기준 정류장", description="예시: 한양대컨벤션센터")
    realtime: list[BusRealtimeItem] = Field(alias="realtime", title="실시간 도착 정보")
    timetable: BusTimetable = Field(alias="timetable", title="시점 출발 시간표")


class BusStopInformationResponse(BaseModel):
    departure_list: list[BusDepartureByLine] = Field(alias="departureInfoList", title="노선별 도착 정보")
