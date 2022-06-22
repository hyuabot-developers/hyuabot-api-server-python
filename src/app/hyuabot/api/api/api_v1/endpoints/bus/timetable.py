from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.hyuabot.api.api.api_v1.endpoints.bus import convert_bus_timetable_item
from app.hyuabot.api.models.postgresql import bus as db
from app.hyuabot.api.schemas.bus import BusTimetable
from app.hyuabot.api.utlis.fastapi import get_db_session

timetable_router = APIRouter(prefix="/timetable")


@timetable_router.get("/{route_id}", status_code=200, response_model=BusTimetable)
async def fetch_bus_timetable(route_id: str, db_session: Session = Depends(get_db_session)):
    route_item = db_session.query(db.BusRoute).filter(db.BusRoute.route_name == route_id).one_or_none()
    if route_item is None:
        return JSONResponse(status_code=404, content={"message": "존재하지 않는 노선입니다."})
    timetable_items: list[db.BusTimetable] = db_session.query(db.BusTimetable) \
        .filter(db.BusTimetable.route_id == route_item.gbis_id).all()
    return BusTimetable(
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
            ),
        ),
    )
