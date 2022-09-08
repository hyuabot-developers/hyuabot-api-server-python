import asyncio
import csv
import json
from datetime import datetime, timezone, timedelta, time

from aiohttp import ClientSession
from korean_lunar_calendar import KoreanLunarCalendar
from sqlalchemy.orm import Session

from app.hyuabot.api.models.postgresql.bus import BusRoute, BusStop, BusTimetable
from app.hyuabot.api.models.postgresql.cafeteria import Cafeteria
from app.hyuabot.api.models.postgresql.campus import Campus
from app.hyuabot.api.models.postgresql.reading_room import ReadingRoom
from app.hyuabot.api.models.postgresql.shuttle import ShuttlePeriod, ShuttleTimetable
from app.hyuabot.api.models.postgresql.subway import SubwayRoute, SubwayStation, SubwayTimetable


def insert_campus_items(db_session: Session):
    campuses = [Campus(campus_name='서울', campus_id=0), Campus(campus_name='ERICA', campus_id=1)]
    db_session.query(Campus).delete()
    db_session.add_all(campuses)
    db_session.commit()


def insert_cafetaria_items(db_session: Session):
    cafeteria_list = [
        Cafeteria(cafeteria_id='1', campus_id=0, cafeteria_name='학생식당'),
        Cafeteria(cafeteria_id='2', campus_id=0, cafeteria_name='생활과학관 식당'),
        Cafeteria(cafeteria_id='4', campus_id=0, cafeteria_name='신소재공학관 식당'),
        Cafeteria(cafeteria_id='6', campus_id=0, cafeteria_name='제1생활관식당'),
        Cafeteria(cafeteria_id='7', campus_id=0, cafeteria_name='제2생활관식당'),
        Cafeteria(cafeteria_id='8', campus_id=0, cafeteria_name='행원파크'),
        Cafeteria(cafeteria_id='11', campus_id=1, cafeteria_name='교직원식당'),
        Cafeteria(cafeteria_id='12', campus_id=1, cafeteria_name='학생식당'),
        Cafeteria(cafeteria_id='13', campus_id=1, cafeteria_name='창의인재원식당'),
        Cafeteria(cafeteria_id='14', campus_id=1, cafeteria_name='푸드코트'),
        Cafeteria(cafeteria_id='15', campus_id=1, cafeteria_name='창업보육센터'),
    ]
    db_session.query(Cafeteria).delete()
    db_session.add_all(cafeteria_list)


def insert_reading_room_items(db_session: Session):
    reading_room_list = [
        ReadingRoom(room_name='HOLMZ 열람석', campus_id=0),
        ReadingRoom(room_name='제1열람실[지하1층]', campus_id=0),
        ReadingRoom(room_name='제2열람실[지하1층]', campus_id=0),
        ReadingRoom(room_name='제3열람실[3층]', campus_id=0),
        ReadingRoom(room_name='제3열람실[4층]', campus_id=0),
        ReadingRoom(room_name='법학 대학원열람실[2층]', campus_id=0),
        ReadingRoom(room_name='법학 제1열람실[3층]', campus_id=0),
        ReadingRoom(room_name='법학 제2열람실A[4층]', campus_id=0),
        ReadingRoom(room_name='법학 제2열람실B[4층]', campus_id=0),
        ReadingRoom(room_name='제1열람실 (2F)', campus_id=1),
        ReadingRoom(room_name='제2열람실 (4F)', campus_id=1),
        ReadingRoom(room_name='제3열람실 (4F)', campus_id=1),
    ]
    db_session.query(ReadingRoom).delete()
    db_session.add_all(reading_room_list)


async def insert_shuttle_period_items(db_session: Session):
    url = "https://raw.githubusercontent.com/hyuabot-developers/hyuabot-shuttle-timetable/main/date.json"

    period_items = []
    now = datetime.now(tz=timezone(timedelta(hours=9)))
    async with ClientSession() as session:
        async with session.get(url) as response:
            date_json = json.loads(await response.text())
            for holiday in date_json['holiday']:
                month, day = holiday.split('/')
                if now.month > int(month) or (now.month == int(month) and now.day > int(day)):
                    year = now.year + 1
                else:
                    year = now.year
                period_items.append(
                    ShuttlePeriod(
                        period="holiday",
                        start_date=datetime.fromisoformat(
                            f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)}T00:00:00"),
                        end_date=datetime.fromisoformat(
                            f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)}T23:59:59"),
                    ))
            for calendar_type, holiday_list in date_json['halt'].items():
                for holiday in holiday_list:
                    month, day = holiday.split('/')
                    if calendar_type == "lunar":
                        year = now.year
                    else:
                        if now.month > int(month) or (now.month == int(month) and now.day > int(day)):
                            year = now.year + 1
                        else:
                            year = now.year
                    period_items.append(
                        ShuttlePeriod(
                            period="halt",
                            start_date=datetime.fromisoformat(
                                f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)}T00:00:00"),
                            end_date=datetime.fromisoformat(
                                f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)}T23:59:59"),
                            calendar_type=calendar_type,
                        ))
            for period in ["semester", "vacation", "vacation_session"]:
                for period_item in date_json[period]:
                    start_date = datetime.strptime(period_item['start'], "%m/%d")\
                        .replace(year=now.year, hour=0, minute=0, second=0,
                                 tzinfo=timezone(timedelta(hours=9)))
                    end_date = datetime.strptime(period_item['end'], "%m/%d")\
                        .replace(year=now.year, hour=23, minute=59, second=59,
                                 tzinfo=timezone(timedelta(hours=9)))
                    if start_date < end_date:
                        if now > end_date:
                            start_date = start_date.replace(year=now.year + 1)
                            end_date = end_date.replace(year=now.year + 1)
                    else:
                        if now < end_date:
                            start_date = start_date.replace(year=now.year - 1)
                        else:
                            end_date = end_date.replace(year=now.year + 1)
                    period_items.append(
                        ShuttlePeriod(
                            period=period,
                            start_date=start_date,
                            end_date=end_date,
                            calendar_type=calendar_type,
                        ))

    db_session.query(ShuttlePeriod).delete()
    db_session.add_all(period_items)
    await insert_shuttle_timetable_items(db_session)


async def insert_shuttle_timetable_items(db_session: Session):
    term_keys = ["semester", "vacation", "vacation_session"]
    day_keys = ["week", "weekend"]

    tasks = []
    db_session.query(ShuttleTimetable).delete()
    for term in term_keys:
        for day in day_keys:
            tasks.append(fetch_shuttle_timetable(db_session, term, day))
    await asyncio.gather(*tasks)


async def fetch_shuttle_timetable(db_session: Session, period: str, day: str):
    base_url = "https://raw.githubusercontent.com/hyuabot-developers/hyuabot-shuttle-timetable/main"
    url = f"{base_url}/{period}/{day}.csv"
    day_dict = {"week": "weekdays", "weekend": "weekends"}
    timetable: list[ShuttleTimetable] = []
    async with ClientSession() as session:
        async with session.get(url) as response:
            reader = csv.reader((await response.text()).splitlines(), delimiter=",")
            for shuttle_type, shuttle_time, shuttle_start_stop in reader:
                timetable.append(
                    ShuttleTimetable(
                        period=period,
                        weekday=day_dict[day],
                        shuttle_type=shuttle_type,
                        shuttle_time=shuttle_time,
                        start_stop=shuttle_start_stop,
                    ),
                )
    db_session.add_all(timetable)


def insert_subway_route_items(db_session: Session):
    route_list = [
        SubwayRoute(route_name="4호선", route_id=1004),
        SubwayRoute(route_name="수인분당선", route_id=1075),
    ]
    db_session.query(SubwayRoute).delete()
    db_session.add_all(route_list)


def insert_subway_station_items(db_session: Session):
    station_list = [
        SubwayStation(station_name="한대앞"),
    ]
    db_session.query(SubwayStation).delete()
    db_session.add_all(station_list)


async def insert_subway_timetable_items(db_session: Session):
    route_list = ["4호선", "수인분당선"]
    weekday_list = ["weekdays", "weekends"]
    heading_list = ["up", "down"]
    station_list = ["한대앞"]

    tasks = []
    db_session.query(SubwayTimetable).delete()
    for station_name in station_list:
        for route_name in route_list:
            for weekday in weekday_list:
                for heading in heading_list:
                    tasks.append(
                        fetch_subway_timetable_items(
                            db_session, station_name, route_name, weekday, heading),
                    )
    await asyncio.gather(*tasks)


async def fetch_subway_timetable_items(
        db_session: Session, station_name: str, route_name: str, weekday: str, heading: str):
    base_url = "https://raw.githubusercontent.com/hyuabot-developers/hyuabot-subway-timetable/main"
    route_color_dict = {"4호선": "skyblue", "수인분당선": "yellow"}
    url = f"{base_url}/{route_color_dict[route_name]}/{weekday}/{heading}.csv"

    async with ClientSession() as session:
        async with session.get(url) as response:
            reader = csv.reader((await response.text()).splitlines(), delimiter=",")
            timetable: list[SubwayTimetable] = []
            for terminal_station, departure_time in reader:
                timetable.append(SubwayTimetable(
                    route_name=route_name,
                    station_name=station_name,
                    heading=heading,
                    weekday=weekday,
                    terminal_station=terminal_station,
                    departure_time=departure_time,
                ))
    db_session.add_all(timetable)


def insert_bus_route_items(db_session: Session):
    route_list = [
        BusRoute(
            route_name="10-1", gbis_id=216000068,
            start_stop="푸르지오6차후문", terminal_stop="상록수역", time_from_start_stop=11),
        BusRoute(
            route_name="707-1", gbis_id=216000070,
            start_stop="신안산대", terminal_stop="수원역", time_from_start_stop=23),
        BusRoute(
            route_name="3102", gbis_id=216000061,
            start_stop="새솔고", terminal_stop="강남역", time_from_start_stop=28),
    ]
    db_session.query(BusRoute).delete()
    db_session.add_all(route_list)


def insert_bus_station_items(db_session: Session):
    station_list = [
        BusStop(stop_name="한양대게스트하우스", gbis_id=216000379),
        BusStop(stop_name="한양대정문", gbis_id=216000719),
    ]
    db_session.query(BusStop).delete()
    db_session.add_all(station_list)


async def insert_bus_timetable_items(db_session: Session):
    weekday_list = ["weekdays", "saturday", "sunday"]
    route_list = ["10-1", "707-1", "3102"]

    tasks = []
    db_session.query(BusTimetable).delete()
    for route_name in route_list:
        for weekday in weekday_list:
            tasks.append(fetch_bus_timetable(db_session, route_name, weekday))

    await asyncio.gather(*tasks)


async def fetch_bus_timetable(db_session: Session, route_name: str, weekday: str):
    base_url = "https://raw.githubusercontent.com/hyuabot-developers/hyuabot-bus-timetable/main"
    url = f"{base_url}/{route_name}/{weekday}/timetable.csv"
    route_id = db_session.query(BusRoute).filter(BusRoute.route_name == route_name)\
        .one_or_none().gbis_id
    timetable: list[BusTimetable] = []
    async with ClientSession() as session:
        async with session.get(url) as response:
            reader = csv.reader((await response.text()).splitlines(), delimiter=",")
            for row in reader:
                departure_time: time = datetime.strptime(row[0], "%H:%M").time()
                timetable.append(
                    BusTimetable(route_id=route_id, weekday=weekday, departure_time=departure_time))
    db_session.add_all(timetable)
    db_session.commit()


async def initialize_data(db_session: Session):
    insert_campus_items(db_session)
    insert_cafetaria_items(db_session)
    insert_reading_room_items(db_session)
    insert_subway_route_items(db_session)
    insert_subway_station_items(db_session)
    insert_bus_route_items(db_session)
    insert_bus_station_items(db_session)
    await insert_shuttle_period_items(db_session)
    await insert_subway_timetable_items(db_session)
    await insert_bus_timetable_items(db_session)
    db_session.commit()
