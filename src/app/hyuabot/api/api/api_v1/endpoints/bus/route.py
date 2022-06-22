from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.hyuabot.api.api.api_v1.endpoints.bus import timetable_limit, convert_bus_realtime_item, \
    convert_bus_timetable_item
from app.hyuabot.api.models.postgresql import bus as db
from app.hyuabot.api.schemas.bus import BusDepartureByLine, BusTimetable, BusStopInformationResponse
from app.hyuabot.api.utlis.fastapi import get_db_session

arrival_router = APIRouter(prefix="/arrival")
start_stop_dict = {"10-1": "푸르지오6차후문", "707-1": "신안산대학교", "3102": "새솔고"}


@arrival_router.get("", status_code=200, response_model=BusStopInformationResponse)
async def fetch_bus_information(
        db_session: Session = Depends(get_db_session)) -> BusStopInformationResponse:
    route_items = db_session.query(db.BusRoute).all()
    realtime_items: list[db.BusRealtime] = db_session.query(db.BusRealtime).all()
    timetable_items: list[db.BusTimetable] = db_session.query(db.BusTimetable).all()

    message = "정상 처리되었습니다."
    departure_items = []
    for route_item in route_items:
        departure_items.append(
            BusDepartureByLine(
                message=message,
                name=route_item.route_name,
                busStop=start_stop_dict[route_item.route_name],
                startStop=route_item.start_stop,
                terminalStop=route_item.terminal_stop,
                timeFromStartStop=route_item.time_from_start_stop,
                realtime=convert_bus_realtime_item(
                    list(filter(lambda x: x.route_id == route_item.gbis_id, realtime_items))
                ),
                timetable=BusTimetable(
                    weekdays=convert_bus_timetable_item(
                        list(
                            filter(
                                lambda x: x.route_id == route_item.gbis_id and x.weekday == "weekdays",
                                timetable_items
                            )
                        )
                    ),
                    saturday=convert_bus_timetable_item(
                        list(
                            filter(
                                lambda x: x.route_id == route_item.gbis_id and x.weekday == "saturday",
                                timetable_items
                            )
                        )
                    ),
                    sunday=convert_bus_timetable_item(
                        list(
                            filter(
                                lambda x: x.route_id == route_item.gbis_id and x.weekday == "sunday",
                                timetable_items
                            )
                        )
                    ),
                )
            )
        )

    return BusStopInformationResponse(departureInfoList=departure_items)


@arrival_router.get("/route/{route_id}", status_code=200, response_model=BusDepartureByLine)
async def fetch_bus_information_by_route(
        route_id: str, timetable_count: int | None = timetable_limit,
        db_session: Session = Depends(get_db_session)):
    route_item = db_session.query(db.BusRoute).filter(db.BusRoute.route_name == route_id).one_or_none()
    if route_item is None:
        return JSONResponse(status_code=404, content={"message": "존재하지 않는 노선입니다."})
    realtime_items: list[db.BusRealtime] = db_session.query(db.BusRealtime) \
        .filter(db.BusRealtime.route_id == route_item.gbis_id).all()
    timetable_items: list[db.BusTimetable] = db_session.query(db.BusTimetable) \
        .filter(db.BusTimetable.route_id == route_item.gbis_id).all()
    message = "정상 처리되었습니다."
    return BusDepartureByLine(
        message=message,
        name=route_item.route_name,
        busStop=start_stop_dict[route_item.route_name],
        startStop=route_item.start_stop,
        terminalStop=route_item.terminal_stop,
        timeFromStartStop=route_item.time_from_start_stop,
        realtime=convert_bus_realtime_item(
            list(filter(lambda x: x.route_id == route_item.gbis_id, realtime_items))
        ),
        timetable=BusTimetable(
            weekdays=convert_bus_timetable_item(
                list(
                    filter(
                        lambda x: x.route_id == route_item.gbis_id and x.weekday == "weekdays",
                        timetable_items
                    )
                )
            )[:timetable_count],
            saturday=convert_bus_timetable_item(
                list(
                    filter(
                        lambda x: x.route_id == route_item.gbis_id and x.weekday == "saturday",
                        timetable_items
                    )
                )
            )[:timetable_count],
            sunday=convert_bus_timetable_item(
                list(
                    filter(
                        lambda x: x.route_id == route_item.gbis_id and x.weekday == "sunday",
                        timetable_items
                    )
                )[:timetable_count],
            ),
        )
    )
