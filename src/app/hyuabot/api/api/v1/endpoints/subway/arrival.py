from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.hyuabot.api.core.date import korea_standard_time
from app.hyuabot.api.models.postgresql.subway import SubwayRoute, SubwayTimetable, SubwayRealtime
from app.hyuabot.api.schemas.subway import \
    SubwayDepartureResponse, SubwayDepartureByLine, SubwayTimetableItem, SubwayRealtimeItem, \
    SubwayRealtimeList, SubwayTimetableList
from app.hyuabot.api.utlis.fastapi import get_db_session

arrival_router = APIRouter(prefix="/arrival")


def convert_subway_timetable_items(
        timetable_items: list[SubwayTimetable], after: bool = True) -> list[SubwayTimetableItem]:
    if after:
        now = datetime.now(tz=korea_standard_time)
        return [
            SubwayTimetableItem(
                departureTime=str(timetable_item.departure_time),
                terminalStation=timetable_item.terminal_station,
            )
            for timetable_item in timetable_items
            if timetable_item.departure_time.hour < 5 or timetable_item.departure_time > now.time()]
    return [
        SubwayTimetableItem(
            departureTime=str(timetable_item.departure_time),
            terminalStation=timetable_item.terminal_station,
        ) for timetable_item in timetable_items]


def convert_subway_realtime_items(realtime_items: list[SubwayRealtime]) -> list[SubwayRealtimeItem]:
    return [
        SubwayRealtimeItem(
            trainNumber=realtime_item.train_number,
            updateTime=realtime_item.update_time,
            isLastTrain=realtime_item.last_train,
            terminalStation=realtime_item.terminal_station,
            currentStation=realtime_item.current_station,
            remainedTime=realtime_item.remained_time,
            statusCode=realtime_item.status,
        ) for realtime_item in realtime_items]


@arrival_router.get("/{campus_name}", status_code=200, response_model=SubwayDepartureResponse)
async def fetch_subway_information(campus_name: str, db_session: Session = Depends(get_db_session)):
    campus_station_dict = {"ERICA": "한대앞"}
    if campus_name.upper() not in campus_station_dict.keys():
        raise HTTPException(status_code=404, detail="Campus name is invalid")
    station_name = campus_station_dict[campus_name.upper()]
    route_list = db_session.query(SubwayRoute).all()
    departure_list = []
    now = datetime.now(tz=korea_standard_time)
    if now.weekday() == 5 or now.weekday() == 6:
        weekday_key = "weekends"
    else:
        weekday_key = "weekdays"

    for route_item in route_list:
        departure_list.append(
            SubwayDepartureByLine(
                lineName=route_item.route_name,
                realtime=SubwayRealtimeList(
                    up=convert_subway_realtime_items(
                        db_session.query(SubwayRealtime).filter(
                            and_(
                                SubwayRealtime.route_name == route_item.route_name,
                                SubwayRealtime.heading == "up"),
                        ).order_by(SubwayRealtime.remained_time).all()),
                    down=convert_subway_realtime_items(
                        db_session.query(SubwayRealtime).filter(
                            and_(
                                SubwayRealtime.route_name == route_item.route_name,
                                SubwayRealtime.heading == "down"),
                        ).order_by(SubwayRealtime.remained_time).all()),
                ),
                timetable=SubwayTimetableList(
                    up=convert_subway_timetable_items(
                        db_session.query(SubwayTimetable).filter(
                            and_(
                                SubwayTimetable.route_name == route_item.route_name,
                                SubwayTimetable.weekday == weekday_key,
                                SubwayTimetable.heading == "up")).all()),
                    down=convert_subway_timetable_items(
                        db_session.query(SubwayTimetable).filter(
                            and_(
                                SubwayTimetable.route_name == route_item.route_name,
                                SubwayTimetable.weekday == weekday_key,
                                SubwayTimetable.heading == "down")).all()),
                ),
            ),
        )
    return SubwayDepartureResponse(
        stationName=station_name,
        departureList=departure_list,
    )
