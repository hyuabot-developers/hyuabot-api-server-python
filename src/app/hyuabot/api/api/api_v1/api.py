from fastapi import APIRouter


from app.hyuabot.api.api.api_v1.endpoints.shuttle import route, stop, location, arrival

shuttle_router = APIRouter(prefix="/shuttle")
shuttle_router.include_router(route.route_router, tags=["Shuttle Route"])
shuttle_router.include_router(stop.stop_router, tags=["Shuttle Stop"])
shuttle_router.include_router(location.location_router, tags=["Shuttle Location"])
shuttle_router.include_router(arrival.arrival_router, tags=["Shuttle Arrival"])
