from fastapi import APIRouter


from app.hyuabot.api.api.api_v1.endpoints import shuttle


shuttle_router = APIRouter()
shuttle_router.include_router(shuttle.router, prefix="/shuttle", tags=["shuttle"])