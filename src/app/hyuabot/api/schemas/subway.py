from datetime import time
from pydantic import BaseModel, Field


class SubwayRealtimeItem(BaseModel):
    updated_time: time = Field(alias="updatedTime", title="도착 정보 갱신 시간",
                               description="예시: '2020-01-01T00:00:00'")
    terminal_station: str = Field(alias="terminalStation", title="행선지(역)", description="예시: '오이도'")
    current_station: str = Field(alias="location", title="현재 위치(역)", description="예시: '반월'")
    remained_time: float = Field(alias="remainedTime", title="남은 시간(분)", description="예시: '10.0'")
    status: str = Field(alias="status", title="상태", description="예시: '출발'")


class SubwayTimetableItem(BaseModel):
    terminal_station: str = Field(alias="terminalStation", title="행선지(역)", description="예시: '오이도'")
    departure_time: float = Field(alias="time", title="출발 시간", description="예시: '20:00:00'")


class SubwayRealtimeList(BaseModel):
    up_line: list[SubwayRealtimeItem] = Field(alias="up", title="상행 실시간 도착 정보")
    down_line: list[SubwayRealtimeItem] = Field(alias="down", title="하행 실시간 도착 정보")


class SubwayTimetableList(BaseModel):
    up_line: list[SubwayTimetableItem] = Field(alias="up", title="상행 출발 시간표")
    down_line: list[SubwayTimetableItem] = Field(alias="down", title="하행 출발 시간표")


class SubwayDepartureByLine(BaseModel):
    line_name: str = Field(alias="lineName", title="노선명", description="예시: '4호선'")
    realtime: SubwayRealtimeList = Field(alias="realtime", title="실시간 도착 정보")
    timetable: SubwayTimetableList = Field(alias="timetable", title="출발 시간표")


class SubwayDepartureResponse(BaseModel):
    station_name: str = Field(alias="stationName", title="역명", description="예시: '한대앞'")
    departure_list: list[SubwayDepartureByLine] = Field(alias="departure_list", title="노선별 출발 정보")
