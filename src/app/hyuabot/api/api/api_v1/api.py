from fastapi import APIRouter


from app.hyuabot.api.api.api_v1.endpoints.shuttle import route, stop


shuttle_router = APIRouter(prefix="/shuttle")
shuttle_router.include_router(route.route_router, tags=["Shuttle Route"])
shuttle_router.include_router(stop.stop_router, tags=["Shuttle Stop"])
