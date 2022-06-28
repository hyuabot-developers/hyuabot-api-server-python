import strawberry
from sqlalchemy import and_
from sqlalchemy.orm import Session
from strawberry.types import Info

from app.hyuabot.api.api.v2.reading_room import ReadingRoomItem
from app.hyuabot.api.api.v2.shuttle import Shuttle
from app.hyuabot.api.api.v2.subway import Subway
from app.hyuabot.api.models.postgresql.reading_room import ReadingRoom


@strawberry.type
class Query:
    @strawberry.field
    def shuttle(self) -> Shuttle:
        return Shuttle()

    @strawberry.field
    def subway(self) -> Subway:
        return Subway()

    @strawberry.field
    def reading_room(self, info: Info, room_name: str = None, campus_id: int = None,
                     is_active: bool = True) -> list[ReadingRoomItem]:
        db_session: Session = info.context["db_session"]
        query = db_session.query(ReadingRoom) \
            .filter(and_(
                ReadingRoom.room_name == room_name if room_name else True,
                ReadingRoom.campus_id == campus_id if campus_id else True,
                ReadingRoom.is_active == is_active,
            )).all()
        result: list[ReadingRoomItem] = []
        for x in query:  # type: ReadingRoom
            result.append(
                ReadingRoomItem(
                    room_name=x.room_name,
                    campus_id=x.campus_id,
                    is_active=x.is_active,
                    is_reservable=x.is_reservable,
                    total_seat=x.total_seat,
                    active_seat=x.active_seat,
                    occupied_seat=x.occupied_seat,
                    available_seat=x.available_seat,
                )
            )
        return result
