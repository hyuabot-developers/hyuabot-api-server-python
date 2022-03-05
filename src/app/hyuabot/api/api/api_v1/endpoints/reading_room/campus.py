import json

from fastapi import APIRouter

from app.hyuabot.api.api.api_v1.endpoints.reading_room import campus_query
from app.hyuabot.api.core.database import get_redis_connection, get_redis_value
from app.hyuabot.api.schemas.reading_room import ReadingRoomItem


reading_room_router = APIRouter(prefix="/library")


@reading_room_router.get("", status_code=200, response_model=list[ReadingRoomItem])
async def fetch_reading_room_by_campus(campus_name: str = campus_query):
    redis_connection = await get_redis_connection("reading_room")
    key = f"{campus_name.lower()}_reading_room"
    json_string: bytes = await get_redis_value(redis_connection, key)
    reading_room_list: list[ReadingRoomItem] = json.loads(json_string.decode("utf-8"))
    return reading_room_list
