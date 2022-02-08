from datetime import time
from pydantic import BaseModel, Field


class SubwayRealtimeItem(BaseModel):
    updated_time: time = Field(alias="updatedTime")
    terminal_station: str = Field(alias="terminalStation")
    current_station: str = Field(alias="location")
    remained_time: float = Field(alias="remainedTime")
    status: str


class SubwayTimetableItem(BaseModel):
    terminal_station: str = Field(alias="terminalStation")
    departure_time: float = Field(alias="time")


class SubwayRealtimeList(BaseModel):
    up_line: list[SubwayRealtimeItem] = Field(alias="up")  # 상행선 실시간 도착 정보 목록
    down_line: list[SubwayRealtimeItem] = Field(alias="down")  # 하행선 실시간 도착 정보 목록


class SubwayTimetableList(BaseModel):
    up_line: list[SubwayTimetableItem] = Field(alias="up")  # 상행선 도착 시간 목록
    down_line: list[SubwayTimetableItem] = Field(alias="down")  # 하행선 도착 시간 목록


class SubwayDepartureByLine(BaseModel):
    line_name: str = Field(alias="lineName")  # 노선명
    realtime: SubwayRealtimeList  # 노선별 실시간 도착 정보
    timetable: SubwayTimetableList  # 노선별 시간표 도착 정보


class SubwayDepartureResponse(BaseModel):
    station_name: str = Field(alias="stationName")  # 역명
    departure_list: list[SubwayDepartureByLine] = Field(alias="departure_list")  # 노선별 도착 정보 목록
