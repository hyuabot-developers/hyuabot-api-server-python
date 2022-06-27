import asyncio
from datetime import datetime, timedelta
from typing import Tuple

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.hyuabot.api.api.v1.endpoints.shuttle import shuttle_stop_type
from app.hyuabot.api.core.date import get_shuttle_term, korea_standard_time
from app.hyuabot.api.models.postgresql import shuttle as db
from app.hyuabot.api.schemas.shuttle import ShuttleDepartureByStop, ShuttleDepartureItem, \
    ShuttleDeparture, ShuttleDepartureTimetable, ShuttleTimetableOnly
from app.hyuabot.api.utlis.fastapi import get_db_session

arrival_router = APIRouter(prefix="/arrival")
shuttle_stop_dict = {"Dormitory": "기숙사", "Shuttlecock_O": "셔틀콕", "Station": "한대앞",
                     "Terminal": "예술인A", "Shuttlecock_I": "셔틀콕 건너편"}


def compare_timetable(shuttle_time: datetime, now: datetime) -> bool:
    shuttle_time = shuttle_time.replace(year=now.year, month=now.month, day=now.day)
    return shuttle_time > now


async def fetch_timetable_by_stop(db_session: Session, shuttle_stop: str, period: str,
                                  weekdays_keys: str, get_all: bool = False) -> \
        Tuple[list[ShuttleDepartureItem], list[ShuttleDepartureItem]]:
    now = datetime.now(tz=korea_standard_time)
    timetable = db_session.query(db.ShuttleTimetable).filter(and_(
        db.ShuttleTimetable.weekday == weekdays_keys,
        db.ShuttleTimetable.period == period,
    )).all()
    shuttle_for_station: list[ShuttleDepartureItem] = []
    shuttle_for_terminal: list[ShuttleDepartureItem] = []
    for shuttle_item in timetable:  # type: db.ShuttleTimetable
        shuttle_departure_time = now.replace(
            hour=shuttle_item.shuttle_time.hour, minute=shuttle_item.shuttle_time.minute)
        shuttle_heading = shuttle_item.shuttle_type
        if shuttle_stop == "Dormitory" and shuttle_item.start_stop == "Dormitory":
            timedelta_minute = -5
            shuttle_departure_time += timedelta(minutes=timedelta_minute)
            if get_all or compare_timetable(shuttle_departure_time, now):
                if shuttle_heading == "DH":
                    shuttle_for_station.append(ShuttleDepartureItem(
                        time=shuttle_departure_time.strftime("%H:%M"), type=shuttle_item.shuttle_type,
                    ))
                elif shuttle_heading == "DY":
                    shuttle_for_terminal.append(ShuttleDepartureItem(
                        time=shuttle_departure_time.strftime("%H:%M"), type=shuttle_item.shuttle_type,
                    ))
                elif shuttle_heading == "C":
                    shuttle_for_station.append(ShuttleDepartureItem(
                        time=shuttle_departure_time.strftime("%H:%M"), type=shuttle_item.shuttle_type,
                    ))
                    shuttle_for_terminal.append(ShuttleDepartureItem(
                        time=shuttle_departure_time.strftime("%H:%M"), type=shuttle_item.shuttle_type,
                    ))
        elif shuttle_stop == "Shuttlecock_O":
            timedelta_minute = 0
            shuttle_departure_time += timedelta(minutes=timedelta_minute)
            if get_all or compare_timetable(shuttle_departure_time, now):
                if shuttle_heading == "DH":
                    shuttle_for_station.append(ShuttleDepartureItem(
                        time=shuttle_departure_time.strftime("%H:%M"), type=shuttle_item.shuttle_type,
                    ))
                elif shuttle_heading == "DY":
                    shuttle_for_terminal.append(ShuttleDepartureItem(
                        time=shuttle_departure_time.strftime("%H:%M"), type=shuttle_item.shuttle_type,
                    ))
                elif shuttle_heading == "C":
                    shuttle_for_station.append(ShuttleDepartureItem(
                        time=shuttle_departure_time.strftime("%H:%M"), type=shuttle_item.shuttle_type,
                    ))
                    shuttle_for_terminal.append(ShuttleDepartureItem(
                        time=shuttle_departure_time.strftime("%H:%M"), type=shuttle_item.shuttle_type,
                    ))
        elif shuttle_stop == "Station":
            timedelta_minute = 10
            shuttle_departure_time += timedelta(minutes=timedelta_minute)
            if get_all or compare_timetable(shuttle_departure_time, now):
                if shuttle_heading == "DH":
                    shuttle_for_station.append(ShuttleDepartureItem(
                        time=shuttle_departure_time.strftime("%H:%M"), type=shuttle_item.shuttle_type,
                    ))
                elif shuttle_heading == "C":
                    shuttle_for_station.append(ShuttleDepartureItem(
                        time=shuttle_departure_time.strftime("%H:%M"), type=shuttle_item.shuttle_type,
                    ))
                    shuttle_for_terminal.append(ShuttleDepartureItem(
                        time=shuttle_departure_time.strftime("%H:%M"), type=shuttle_item.shuttle_type,
                    ))
        elif shuttle_stop == "Terminal":
            if shuttle_heading == "DY":
                timedelta_minute = 10
                shuttle_departure_time += timedelta(minutes=timedelta_minute)
                if get_all or compare_timetable(shuttle_departure_time, now):
                    shuttle_for_terminal.append(ShuttleDepartureItem(
                        time=shuttle_departure_time.strftime("%H:%M"), type=shuttle_item.shuttle_type,
                    ))
            elif shuttle_heading == "C":
                timedelta_minute = 15
                shuttle_departure_time += timedelta(minutes=timedelta_minute)
                if get_all or compare_timetable(shuttle_departure_time, now):
                    shuttle_for_terminal.append(ShuttleDepartureItem(
                        time=shuttle_departure_time.strftime("%H:%M"), type=shuttle_item.shuttle_type,
                    ))
        elif shuttle_stop == "Shuttlecock_I" or shuttle_item.start_stop == "Dormitory":
            if shuttle_heading == "DH" or shuttle_heading == "DY":
                timedelta_minute = 20
            else:
                timedelta_minute = 25
            shuttle_departure_time += timedelta(minutes=timedelta_minute)
            if get_all or compare_timetable(shuttle_departure_time, now):
                shuttle_for_terminal.append(ShuttleDepartureItem(
                    time=shuttle_departure_time.strftime("%H:%M"), type=shuttle_item.shuttle_type,
                ))
    return shuttle_for_station, shuttle_for_terminal


@arrival_router.get("", status_code=200, response_model=ShuttleDeparture)
async def fetch_arrival_list(db_session: Session = Depends(get_db_session)):
    is_working, current_term, weekdays_keys, query_time = await get_shuttle_term(db_session)
    if not is_working:
        return JSONResponse(content={
            "message": "당일은 셔틀을 운행하지 않습니다.",
            "busForStation": [], "busForTerminal": [],
        })

    tasks = []
    for shuttle_stop in shuttle_stop_dict.keys():
        tasks.append(fetch_timetable_by_stop(db_session, shuttle_stop, current_term, weekdays_keys))

    results = []
    for (shuttle_stop_id, shuttle_stop_name), (shuttle_for_station, shuttle_for_terminal) \
            in zip(shuttle_stop_dict.items(), await asyncio.gather(*tasks)):
        results.append(ShuttleDepartureByStop(
            stopName=shuttle_stop_name,
            stopCode=shuttle_stop_id,
            busForStation=shuttle_for_station,
            busForTerminal=shuttle_for_terminal,
        ))
    return ShuttleDeparture(
        queryTime=query_time,
        arrivalList=results,
    )


@arrival_router.get("/{shuttle_stop}", status_code=200, response_model=ShuttleDepartureByStop)
async def fetch_arrival_list_by_stop(shuttle_stop: str, db_session: Session = Depends(get_db_session)):
    if shuttle_stop not in shuttle_stop_type:
        return JSONResponse(status_code=404, content={"message": "존재하지 않는 셔틀버스 정류장입니다."})

    is_working, current_term, weekdays_keys, query_time = await get_shuttle_term(db_session)
    if not is_working:
        return JSONResponse(content={
            "message": "당일은 셔틀을 운행하지 않습니다.",
            "busForStation": [], "busForTerminal": [],
        })
    shuttle_for_station, shuttle_for_terminal = \
        await fetch_timetable_by_stop(db_session, shuttle_stop, current_term, weekdays_keys)
    return ShuttleDepartureByStop(
        stopName=shuttle_stop_dict[shuttle_stop],
        stopCode=shuttle_stop,
        busForStation=shuttle_for_station,
        busForTerminal=shuttle_for_terminal,
    )


@arrival_router.get("/{shuttle_stop}/timetable", status_code=200, response_model=ShuttleDepartureByStop)
async def fetch_timetable_list_by_stop(shuttle_stop: str, db_session: Session = Depends(get_db_session)):
    if shuttle_stop not in shuttle_stop_type:
        return JSONResponse(status_code=404, content={"message": "존재하지 않는 셔틀버스 정류장입니다."})

    is_working, current_term, weekdays_keys, query_time = await get_shuttle_term(db_session)
    if not is_working:
        return JSONResponse(content={
            "message": "당일은 셔틀을 운행하지 않습니다.",
            "busForStation": [], "busForTerminal": [],
        })
    shuttle_for_station, shuttle_for_terminal = \
        await fetch_timetable_by_stop(
            db_session, shuttle_stop, current_term, weekdays_keys, get_all=True)
    return ShuttleDepartureByStop(
        stopName=shuttle_stop_dict[shuttle_stop],
        stopCode=shuttle_stop,
        busForStation=shuttle_for_station,
        busForTerminal=shuttle_for_terminal,
    )


@arrival_router.get("/{shuttle_stop}/timetable/all", status_code=200,
                    response_model=ShuttleDepartureTimetable)
async def fetch_timetable_list_by_stop_all(
        shuttle_stop: str, db_session: Session = Depends(get_db_session)):
    if shuttle_stop not in shuttle_stop_type:
        return JSONResponse(status_code=404, content={"message": "존재하지 않는 셔틀버스 정류장입니다."})

    is_working, current_term, _, query_time = await get_shuttle_term(db_session)
    shuttle_for_station_weekdays, shuttle_for_terminal_weekdays = \
        await fetch_timetable_by_stop(db_session, shuttle_stop, current_term, "weekdays", get_all=True)
    shuttle_for_station_weekends, shuttle_for_terminal_weekends = \
        await fetch_timetable_by_stop(db_session, shuttle_stop, current_term, "weekends", get_all=True)
    return ShuttleDepartureTimetable(
        stopName=shuttle_stop_dict[shuttle_stop],
        stopCode=shuttle_stop,
        weekdays=ShuttleTimetableOnly(
            busForStation=shuttle_for_station_weekdays,
            busForTerminal=shuttle_for_terminal_weekdays,
        ),
        weekends=ShuttleTimetableOnly(
            busForStation=shuttle_for_station_weekends,
            busForTerminal=shuttle_for_terminal_weekends,
        ),
    )
