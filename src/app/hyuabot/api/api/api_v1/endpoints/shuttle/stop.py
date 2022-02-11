from math import sqrt

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.hyuabot.api.schemas.shuttle import ShuttleStop
from app.hyuabot.api.api.api_v1.endpoints.shuttle import shuttle_dormitory, shuttle_shuttlecock_o, \
    shuttle_station, shuttle_terminal, shuttle_shuttlecock_i

stop_router = APIRouter(prefix="/station")


@stop_router.get("/around", status_code=200, response_model=ShuttleStop)
async def fetch_around_shuttle_stop(latitude: float, longitude: float):
    station_list: list[ShuttleStop] = [shuttle_dormitory, shuttle_shuttlecock_o, shuttle_station,
                                       shuttle_terminal, shuttle_shuttlecock_i]
    distance_between_station = [
        sqrt((station.latitude - latitude) ** 2 + (station.longitude - longitude) ** 2)
        for station in station_list
    ]
    around_station = station_list[distance_between_station.index(min(distance_between_station))]
    return JSONResponse(content=around_station.dict())
