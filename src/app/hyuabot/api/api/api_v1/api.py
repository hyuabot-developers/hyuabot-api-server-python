from fastapi import APIRouter


from app.hyuabot.api.api.api_v1.endpoints.shuttle import route


shuttle_router = APIRouter()
shuttle_router.include_router(route.route_router, prefix="/shuttle", tags=["shuttle"])
