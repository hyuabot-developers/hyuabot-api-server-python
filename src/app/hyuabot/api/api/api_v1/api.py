from fastapi import APIRouter


from app.hyuabot.api.api.api_v1.endpoints.shuttle import route as shuttle_route, \
                                                            stop as shuttle_stop, \
                                                            location as shuttle_location, \
                                                            arrival as shuttle_arrival
from app.hyuabot.api.api.api_v1.endpoints.bus import route as bus_route


shuttle_router = APIRouter(prefix="/shuttle")
shuttle_router.include_router(shuttle_route.route_router, tags=["Shuttle Route"])
shuttle_router.include_router(shuttle_stop.stop_router, tags=["Shuttle Stop"])
shuttle_router.include_router(shuttle_location.location_router, tags=["Shuttle Location"])
shuttle_router.include_router(shuttle_arrival.arrival_router, tags=["Shuttle Arrival"])

bus_router = APIRouter(prefix="/bus")
bus_router.include_router(bus_route.arrival_router, tags=["Bus Route"])
