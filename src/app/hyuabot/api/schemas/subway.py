from datetime import time
from pydantic.main import BaseModel


class SubwayRealtimeItem(BaseModel):
    updatedTime: time
    terminalStation: str
    location: str
    remainedTime: float
    status: str


class SubwayTimetableItem(BaseModel):
    terminalStation: str
    time: time


class SubwayRealtimeList(BaseModel):
    up: list[SubwayRealtimeItem]  # 상행선 실시간 도착 정보 목록
    down: list[SubwayRealtimeItem]  # 하행선 실시간 도착 정보 목록


class SubwayTimetableList(BaseModel):
    up: list[SubwayTimetableItem]  # 상행선 도착 시간 목록
    down: list[SubwayTimetableItem]  # 하행선 도착 시간 목록


class SubwayDepartureByLine(BaseModel):
    lineName: str  # 노선명
    realtime: SubwayRealtimeList  # 노선별 실시간 도착 정보
    timetable: SubwayTimetableList  # 노선별 시간표 도착 정보


class SubwayStationInformation(BaseModel):
    stationName: str  # 역명
    departureInfoList: list[SubwayDepartureByLine]  # 노선별 도착 정보 목록
