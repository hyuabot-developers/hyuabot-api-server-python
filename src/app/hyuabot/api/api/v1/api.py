from fastapi import APIRouter

from app.hyuabot.api.api.v1.endpoints.bus import route as bus_route, \
    timetable as bus_timetable
from app.hyuabot.api.api.v1.endpoints.shuttle import route as shuttle_route, \
    stop as shuttle_stop, \
    location as shuttle_location, \
    arrival as shuttle_arrival, \
    timetable as shuttle_timetable
from app.hyuabot.api.api.v1.endpoints.subway import arrival as subway_arrival

shuttle_router = APIRouter(prefix="/shuttle")
shuttle_router.include_router(shuttle_route.route_router, tags=["Shuttle Route"])
shuttle_router.include_router(shuttle_stop.stop_router, tags=["Shuttle Stop"])
shuttle_router.include_router(shuttle_location.location_router, tags=["Shuttle Location"])
shuttle_router.include_router(shuttle_arrival.arrival_router, tags=["Shuttle Arrival"])
shuttle_router.include_router(shuttle_timetable.timetable_router, tags=["Shuttle Timetable"])

bus_router = APIRouter(prefix="/bus")
bus_router.include_router(bus_route.arrival_router, tags=["Bus Route"])
bus_router.include_router(bus_timetable.timetable_router, tags=["Bus Timetable"])

subway_router = APIRouter(prefix="/subway")
subway_router.include_router(subway_arrival.arrival_router, tags=["Subway Arrival"])
