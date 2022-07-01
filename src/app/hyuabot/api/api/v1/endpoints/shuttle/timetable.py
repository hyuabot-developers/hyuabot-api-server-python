import asyncio

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.hyuabot.api.utlis.fastapi import get_db_session
from app.hyuabot.api.api.v1.endpoints.shuttle.arrival import fetch_timetable_list_by_stop_all
from app.hyuabot.api.core.date import get_shuttle_term
from app.hyuabot.api.schemas.shuttle import ShuttleTimetable

timetable_router: APIRouter = APIRouter(prefix="/timetable")
shuttle_stop_dict = {"Dormitory": "기숙사", "Shuttlecock_O": "셔틀콕", "Station": "한대앞",
                     "Terminal": "예술인A", "Shuttlecock_I": "셔틀콕 건너편"}


@timetable_router.get("", status_code=200, response_model=ShuttleTimetable)
async def fetch_timetable_list_by_stop(db_session=Depends(get_db_session)):
    is_working, current_term, weekdays_keys, query_time = await get_shuttle_term(db_session)
    if not is_working:
        return JSONResponse(content={
            "message": "당일은 셔틀을 운행하지 않습니다.",
            "busForStation": [], "busForTerminal": [],
        })

    tasks = []
    for shuttle_stop in shuttle_stop_dict.keys():
        tasks.append(fetch_timetable_list_by_stop_all(shuttle_stop))

    results = []
    for shuttle_timetable_by_stop in await asyncio.gather(*tasks):
        results.append(shuttle_timetable_by_stop)
    return ShuttleTimetable(
        queryTime=query_time,
        timetableList=results,
    )
