from fastapi import APIRouter

from app.hyuabot.api.core.date import get_shuttle_term
from app.hyuabot.api.schemas.shuttle import ShuttleDepartureByStop

router = APIRouter()


@router.get("/shuttle/{shuttle_stop_code}", status_code=200, response_model=ShuttleDepartureByStop)
async def fetch_shuttle_info(shuttle_stop_code: str):
    is_working, current_term = await get_shuttle_term()
    if not is_working:
        return {"busForStation": [], "busForTerminal": []}
    return {"busForStation": [], "busForTerminal": []}
