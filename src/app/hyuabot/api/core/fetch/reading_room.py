import asyncio

import aiohttp
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.hyuabot.api.models.postgresql.reading_room import ReadingRoom
from app.hyuabot.api.utlis.fastapi import get_db_session

fetch_reading_room_router = APIRouter(prefix="/library")
campus_id_dict = {
    "seoul": 1,
    "erica": 2,
}


@fetch_reading_room_router.get("", status_code=200)
async def fetch_reading_room(db_session: Session = Depends(get_db_session)) -> JSONResponse:
    await fetch_reading_room_api(db_session)
    return JSONResponse({"message": "Fetch reading room data success"}, status_code=200)


async def fetch_reading_room_api(db_session: Session) -> None:
    url = "https://lib.hanyang.ac.kr/smufu-api/pc/0/rooms-at-seat"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response_json = await response.json()
            reading_room_list: list = response_json["data"]["list"]
            for reading_room_result_item in reading_room_list:
                db_session.query(ReadingRoom)\
                    .filter(ReadingRoom.room_name == reading_room_result_item["name"])\
                    .update({
                        "is_active": reading_room_result_item["isActive"],
                        "is_reservable": reading_room_result_item["isReservable"],
                        "total_seat": reading_room_result_item["total"],
                        "active_seat": reading_room_result_item["activeTotal"],
                        "occupied_seat": reading_room_result_item["occupied"],
                        "available_seat": reading_room_result_item["available"],
                    })
    db_session.commit()
