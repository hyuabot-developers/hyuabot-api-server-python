from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.hyuabot.api.models.postgresql.campus import Campus
from app.hyuabot.api.models.postgresql.reading_room import ReadingRoom
from app.hyuabot.api.schemas.reading_room import ReadingRoomItem
from app.hyuabot.api.utlis.fastapi import get_db_session

reading_room_router = APIRouter(prefix="/library")


@reading_room_router.get("/{campus_name}", status_code=200,
                         response_model=list[ReadingRoomItem], tags=["Reading room seat by campus"])
async def fetch_reading_room_by_campus(campus_name: str, db_session: Session = Depends(get_db_session)):
    campus_query = db_session.query(Campus).filter(Campus.campus_name == campus_name).one_or_none()
    if campus_query is None:
        return JSONResponse(status_code=404, content={"message": "존재하지 않는 캠퍼수입니다."})
    campus_id = campus_query.campus_id
    room_query: list[ReadingRoom] = \
        db_session.query(ReadingRoom).filter(ReadingRoom.campus_id == campus_id).all()
    reading_room_list = []
    for reading_room in room_query:
        reading_room_list.append(ReadingRoomItem(
            name=reading_room.room_name,
            isActive=reading_room.is_active,
            isReservable=reading_room.is_reservable,
            total=reading_room.total_seat,
            activeTotal=reading_room.active_seat,
            occupied=reading_room.occupied_seat,
            available=reading_room.available_seat,
        ))
    return reading_room_list
