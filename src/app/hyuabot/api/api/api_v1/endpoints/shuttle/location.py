from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.hyuabot.api.api.api_v1.endpoints.shuttle import shuttle_line_type
from app.hyuabot.api.core.date import get_shuttle_term, korea_standard_time
from app.hyuabot.api.models.postgresql import shuttle as db
from app.hyuabot.api.schemas.shuttle import ShuttleListResponse, ShuttleListItem
from app.hyuabot.api.utlis.fastapi import get_db_session

location_router = APIRouter(prefix="/location")


@location_router.get("/{shuttle_type}", status_code=200, response_model=ShuttleListResponse)
async def fetch_shuttle_location_each_type(
        shuttle_type: str, db_session: Session = Depends(get_db_session)):
    if shuttle_type not in shuttle_line_type:
        return JSONResponse(status_code=404, content={"message": "존재하지 않는 셔틀버스 종류입니다."})

    is_working, current_term, weekdays_keys, query_time = await get_shuttle_term(db_session)
    if not is_working:
        return JSONResponse(content={
            "message": "당일은 셔틀을 운행하지 않습니다.",
            "shuttleList": [],
        })

    now = datetime.now(tz=korea_standard_time)
    timetable = db_session.query(db.ShuttleTimetable).filter(
        and_(
            db.ShuttleTimetable.shuttle_type == shuttle_type,
            db.ShuttleTimetable.period == current_term,
            db.ShuttleTimetable.weekday == weekdays_keys,
        ),
    ).all()
    shuttle_departure_list: list[ShuttleListItem] = []
    now = datetime.now(tz=korea_standard_time)
    if shuttle_type == "DH" or shuttle_type == "DY":
        for shuttle_index, shuttle_item in enumerate(timetable):
            shuttle_departure_time = now.replace(
                hour=shuttle_item.shuttle_time.hour, minute=shuttle_item.shuttle_time.minute)
            if now - timedelta(minutes=30) <= shuttle_departure_time <= now:
                last_bus = False
                if shuttle_departure_time <= now - timedelta(minutes=25):
                    current_station = "셔틀콕 건너편"
                    current_seq = 3
                elif shuttle_departure_time <= now - timedelta(minutes=15):
                    current_station = "한대앞역" if shuttle_departure_time else "예술인"
                    current_seq = 2
                elif shuttle_departure_time <= now - timedelta(minutes=5):
                    current_station = "셔틀콕"
                    current_seq = 1
                else:
                    current_station = "기숙사"
                    current_seq = 0
                if shuttle_index == len(timetable) - 1:
                    last_bus = True

                shuttle_departure_list.append(ShuttleListItem(
                    currentStation=current_station,
                    currentStationSeq=current_seq,
                    lastShuttle=last_bus,
                ))
            elif shuttle_departure_time > now:
                break
    else:
        for shuttle_index, shuttle_item in enumerate(timetable):
            shuttle_departure_time = now.replace(
                hour=shuttle_item.shuttle_time.hour, minute=shuttle_item.shuttle_time.minute)
            if now - timedelta(minutes=35) <= shuttle_departure_time <= now:
                last_bus = False
                if shuttle_departure_time <= now - timedelta(minutes=30):
                    current_station = "셔틀콕 건너편"
                    current_seq = 4
                elif shuttle_departure_time <= now - timedelta(minutes=20):
                    current_station = "예술인"
                    current_seq = 3
                elif shuttle_departure_time <= now - timedelta(minutes=15):
                    current_station = "한대앞역"
                    current_seq = 2
                elif shuttle_departure_time <= now - timedelta(minutes=10):
                    current_station = "셔틀콕"
                    current_seq = 1
                else:
                    current_station = "기숙사"
                    current_seq = 0
                if shuttle_index == len(timetable) - 1:
                    last_bus = True
                shuttle_departure_list.append(ShuttleListItem(
                    currentStation=current_station,
                    currentStationSeq=current_seq,
                    lastShuttle=last_bus,
                ))
            elif shuttle_departure_time > now:
                break
    return ShuttleListResponse(message="정상 처리되었습니다.", shuttleList=shuttle_departure_list)
