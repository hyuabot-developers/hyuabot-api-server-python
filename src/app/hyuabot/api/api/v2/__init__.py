from typing import Optional

import strawberry
from sqlalchemy import and_
from sqlalchemy.orm import Session
from strawberry.types import Info

from app.hyuabot.api.api.v2.bus import BusItem
from app.hyuabot.api.api.v2.cafeteria import CafeteriaItem
from app.hyuabot.api.api.v2.reading_room import ReadingRoomItem
from app.hyuabot.api.api.v2.shuttle import Shuttle
from app.hyuabot.api.api.v2.subway import SubwayItem
from app.hyuabot.api.models.postgresql.bus import BusStop, BusRoute
from app.hyuabot.api.models.postgresql.cafeteria import Cafeteria
from app.hyuabot.api.models.postgresql.reading_room import ReadingRoom


def bus_query(db_session: Session, stop_name: str, route_name: str) -> BusItem | None:
    stop_query: BusStop = \
        db_session.query(BusStop).filter(BusStop.stop_name == stop_name).first()
    route_query: BusRoute = \
        db_session.query(BusRoute).filter(BusRoute.route_name == route_name).first()
    if stop_query is not None and route_query is not None:
        bus_item = BusItem(
            stop_name=stop_name,
            stop_id=stop_query.gbis_id,
            route_name=route_name,
            route_id=route_query.gbis_id,
            start_stop=route_query.start_stop,
            terminal_stop=route_query.terminal_stop,
            time_from_start_stop=route_query.time_from_start_stop,
        )
        return bus_item
    return None


@strawberry.type
class Query:
    @strawberry.input
    class BusQuery:
        stop_name: str
        route_name: str

    @strawberry.input
    class SubwayQuery:
        station_name: str
        route_name: str

    @strawberry.field
    def shuttle(self) -> Shuttle:
        return Shuttle()

    @strawberry.field
    def subway(self, stations: Optional[list[str]] = None, routes: Optional[list[str]] = None,
               route_pair: Optional[list[SubwayQuery]] = None) -> list[SubwayItem]:
        result: list[SubwayItem] = []
        if route_pair is not None:
            for query_item in route_pair:
                result.append(SubwayItem(station_name=query_item.station_name, route_name=query_item.route_name))
        elif stations is not None and routes is not None:
            for station_name in stations:
                for route_name in routes:
                    result.append(SubwayItem(station_name=station_name, route_name=route_name))
        return result

    @strawberry.field
    def bus(self, info: Info, stop_list: Optional[list[str]] = None, routes: Optional[list[str]] = None,
            route_pair: Optional[list[BusQuery]] = None) -> list[BusItem]:
        result: list[BusItem] = []
        db_session: Session = info.context["db_session"]
        if route_pair is not None:
            for query_item in route_pair:
                bus_item = bus_query(db_session, query_item.stop_name, query_item.route_name)
                if bus_item is not None:
                    result.append(bus_item)
        elif stop_list is not None and routes is not None:
            for stop_name in stop_list:
                for route_name in routes:
                    bus_item = bus_query(db_session, stop_name, route_name)
                    if bus_item is not None:
                        result.append(bus_item)
        return result

    @strawberry.field
    def reading_room(self, info: Info, room_name: str | None, campus_id: int | None,
                     is_active: bool = True) -> list[ReadingRoomItem]:
        db_session: Session = info.context["db_session"]
        expressions = [ReadingRoom.is_active == is_active]
        if room_name is not None:
            expressions.append(ReadingRoom.room_name == room_name)
        if campus_id is not None:
            expressions.append(ReadingRoom.campus_id == campus_id)
        query = db_session.query(ReadingRoom) \
            .filter(and_(True, *expressions)).all()
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
                ),
            )
        return result

    @strawberry.field
    def cafeteria(self, info: Info, campus_id: int = None, cafeteria_id_list: list[int] = None) \
            -> list[CafeteriaItem]:
        if cafeteria_id_list is None:
            cafeteria_id_list = []
        db_session: Session = info.context["db_session"]
        expressions = []
        if campus_id is not None:
            expressions.append(Cafeteria.campus_id == campus_id)
        if len(cafeteria_id_list) > 0:
            expressions.append(Cafeteria.id.in_(cafeteria_id_list))
        query = db_session.query(Cafeteria) \
            .filter(and_(True, *expressions)).all()
        result: list[CafeteriaItem] = []
        for x in query:
            result.append(CafeteriaItem(
                cafeteria_id=x.cafeteria_id,
                cafeteria_name=x.cafeteria_name,
            ))
        return result
