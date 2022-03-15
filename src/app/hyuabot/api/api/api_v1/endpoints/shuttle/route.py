from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.hyuabot.api.api.api_v1.endpoints.shuttle import shuttle_dormitory, shuttle_shuttlecock_o, \
    shuttle_station, shuttle_terminal, shuttle_shuttlecock_i
from app.hyuabot.api.api.api_v1.endpoints.shuttle import shuttle_line_type
from app.hyuabot.api.schemas.shuttle import ShuttleRouteStationListResponse

route_router = APIRouter(prefix="/route")


@route_router.get("/station/{shuttle_type}", status_code=200,
                  response_model=ShuttleRouteStationListResponse)
async def fetch_shuttle_route_station_list(shuttle_type: str):
    if shuttle_type not in shuttle_line_type:
        return JSONResponse(status_code=404, content={"message": "존재하지 않는 셔틀버스 종류입니다."})

    message = "정상 처리되었습니다."
    if shuttle_type == "DH":
        station_list = [shuttle_dormitory, shuttle_shuttlecock_o,
                        shuttle_station, shuttle_shuttlecock_i, shuttle_dormitory]
    elif shuttle_type == "DY":
        station_list = [shuttle_dormitory, shuttle_shuttlecock_o,
                        shuttle_terminal, shuttle_shuttlecock_i, shuttle_dormitory]
    else:
        station_list = [shuttle_dormitory, shuttle_shuttlecock_o, shuttle_station,
                        shuttle_terminal, shuttle_shuttlecock_i, shuttle_dormitory]
    return ShuttleRouteStationListResponse(message=message, stationList=station_list)
