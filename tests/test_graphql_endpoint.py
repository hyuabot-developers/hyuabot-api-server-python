from datetime import time

import pytest
from starlette.testclient import TestClient

from app.hyuabot.api import AppSettings
from app.hyuabot.api.main import app

station_list = ["힌대앞"]
subway_route_list = ["4호선", "수인분당선"]
subway_heading_list = ["up", "down"]
subway_weekday_list = ["weekdays", "weekends"]

bus_weekday_list = ["weekdays", "satuday", "sunday"]


@pytest.mark.asyncio
async def test_shuttle_timetable_graphql():
    app_settings = AppSettings()
    with TestClient(app=app) as client:
        query = """query {
            shuttle{
                timetable{
                    period, weekday, shuttleType, shuttleTime, startStop
                }
            }
        }"""
        response = client.post(f"{app_settings.API_V2_STR}", json={"query": query})
        response_json = response.json()
        assert response.status_code == 200
        assert "data" in response_json.keys()
        assert type(response_json["data"]) == dict

        assert "shuttle" in response_json["data"].keys()
        assert type(response_json["data"]["shuttle"]) == dict

        assert "timetable" in response_json["data"]["shuttle"].keys()
        timetable_list = response_json["data"]["shuttle"]["timetable"]
        assert type(timetable_list) == list
        assert len(timetable_list) > 0
        for timetable_item in timetable_list:
            assert "period" in timetable_item.keys() and type(timetable_item["period"]) == str
            assert "weekday" in timetable_item.keys() and type(timetable_item["weekday"]) == str
            assert "shuttleType" in timetable_item.keys() and type(timetable_item["shuttleType"]) == str
            assert "shuttleTime" in timetable_item.keys() and type(timetable_item["shuttleTime"]) == str
            assert "startStop" in timetable_item.keys() and type(timetable_item["startStop"]) == str


@pytest.mark.asyncio
async def test_subway_name_graphql():
    app_settings = AppSettings()
    with TestClient(app=app) as client:
        query = """query {
            subway(stations: [\"한대앞\"], routes: [\"4호선\", \"수인분당선\"]){
                stationName, routeName
            }
        }"""
        response = client.post(f"{app_settings.API_V2_STR}", json={"query": query})
        response_json = response.json()
        assert response.status_code == 200
        assert "data" in response_json.keys()
        assert type(response_json["data"]) == dict

        assert "subway" in response_json["data"].keys()
        assert type(response_json["data"]["subway"]) == list

        subway_list = response_json["data"]["subway"]
        assert len(subway_list) == 2
        for subway_item in subway_list:
            assert "stationName" in subway_item.keys() and type(subway_item["stationName"]) == str
            assert "routeName" in subway_item.keys() and type(subway_item["routeName"]) == str


@pytest.mark.asyncio
async def test_subway_timetable_graphql():
    app_settings = AppSettings()
    with TestClient(app=app) as client:
        for heading in subway_heading_list:
            for weekday in subway_weekday_list:
                query = "query {" \
                        "subway(stations: [\"한대앞\"], routes: [\"4호선\", \"수인분당선\"]){" \
                        f"timetable(heading: \"{heading}\", weekday: \"{weekday}\")" \
                        "{heading, weekday, terminalStation, departureTime}}}"
                response = client.post(f"{app_settings.API_V2_STR}", json={"query": query})
                response_json = response.json()
                assert response.status_code == 200
                assert "data" in response_json.keys()
                assert type(response_json["data"]) == dict

                assert "subway" in response_json["data"].keys()
                assert type(response_json["data"]["subway"]) == list

                subway_list = response_json["data"]["subway"]
                assert len(subway_list) == 2
                for subway_item in subway_list:
                    assert "timetable" in subway_item.keys()
                    timetable_list = subway_item["timetable"]
                    assert type(timetable_list) == list
                    assert len(timetable_list) > 0
                    for timetable_item in timetable_list:
                        assert "heading" in timetable_item.keys() and \
                               type(timetable_item["heading"]) == str
                        assert "weekday" in timetable_item.keys() and \
                               type(timetable_item["weekday"]) == str
                        assert "terminalStation" in timetable_item.keys() and \
                               type(timetable_item["terminalStation"]) == str
                        assert "departureTime" in timetable_item.keys() and \
                               type(timetable_item["departureTime"]) == str


@pytest.mark.asyncio
async def test_subway_realtime_graphql():
    app_settings = AppSettings()
    with TestClient(app=app) as client:
        for heading in subway_heading_list:
            query = "query {" \
                    "subway(stations: [\"한대앞\"], routes: [\"4호선\", \"수인분당선\"]){" \
                    f"realtime(heading: \"{heading}\")" \
                    "{heading, updateTime, trainNumber, lastTrain, terminalStation, currentStation" \
                    "}}}"
            response = client.post(f"{app_settings.API_V2_STR}", json={"query": query})
            response_json = response.json()
            assert response.status_code == 200
            assert "data" in response_json.keys()
            assert type(response_json["data"]) == dict

            assert "subway" in response_json["data"].keys()
            assert type(response_json["data"]["subway"]) == list

            subway_list = response_json["data"]["subway"]
            assert len(subway_list) == 2
            for subway_item in subway_list:
                assert "realtime" in subway_item.keys()
                realtime_list = subway_item["realtime"]
                assert type(realtime_list) == list
                assert len(realtime_list) >= 0
                for realtime_item in realtime_list:
                    assert "heading" in realtime_item.keys() and \
                           type(realtime_item["heading"]) == str
                    assert "updateTime" in realtime_item.keys() and \
                           type(realtime_item["updateTime"]) == str
                    assert "trainNumber" in realtime_item.keys() and \
                           type(realtime_item["trainNumber"]) == str
                    assert "lastTrain" in realtime_item.keys() and \
                           type(realtime_item["lastTrain"]) == str
                    assert "terminalStation" in realtime_item.keys() and \
                           type(realtime_item["terminalStation"]) == str
                    assert "currentStation" in realtime_item.keys() and \
                           type(realtime_item["currentStation"]) == str
                    assert "remainedTime" in realtime_item.keys() and \
                           type(realtime_item["remainedTime"]) == int
                    assert "status" in realtime_item.keys() and \
                           type(realtime_item["status"]) == str


@pytest.mark.asyncio
async def test_bus_information_graphql():
    app_settings = AppSettings()
    with TestClient(app=app) as client:
        query = "query {" \
                "bus(stopList: [\"한양대게스트하우스\", \"한양대정문\"], " \
                "routes: [\"3102\", \"10-1\", \"707-1\"]){stopName, routeName, stopId, routeId," \
                "startStop, terminalStop, timeFromStartStop}}"
        response = client.post(f"{app_settings.API_V2_STR}", json={"query": query})
        response_json = response.json()
        assert response.status_code == 200
        assert "data" in response_json.keys()
        assert type(response_json["data"]) == dict

        assert "bus" in response_json["data"].keys()
        assert type(response_json["data"]["bus"]) == list

        bus_list = response_json["data"]["bus"]
        assert len(bus_list) > 0
        for bus_item in bus_list:
            assert "stopName" in bus_item.keys() and type(bus_item["stopName"]) == str
            assert "routeName" in bus_item.keys() and type(bus_item["routeName"]) == str
            assert "stopId" in bus_item.keys() and type(bus_item["stopId"]) == int
            assert "routeId" in bus_item.keys() and type(bus_item["routeId"]) == int
            assert "startStop" in bus_item.keys() and type(bus_item["startStop"]) == str
            assert "terminalStop" in bus_item.keys() and type(bus_item["terminalStop"]) == str
            assert "timeFromStartStop" in bus_item.keys() and \
                   type(bus_item["timeFromStartStop"]) == int


@pytest.mark.asyncio
async def test_bus_timetable_graphql():
    app_settings = AppSettings()
    with TestClient(app=app) as client:
        for weekday in bus_weekday_list:
            query = "query {" \
                    "bus(stopList: [\"한양대게스트하우스\", \"한양대정문\"], " \
                    "routes: [\"3102\", \"10-1\", \"707-1\"]){" \
                    f"timetable(weekday: \"{weekday}\")" \
                    "{departureTime}}}"
            response = client.post(f"{app_settings.API_V2_STR}", json={"query": query})
            response_json = response.json()
            assert response.status_code == 200
            assert "data" in response_json.keys()
            assert type(response_json["data"]) == dict

            assert "bus" in response_json["data"].keys()
            assert type(response_json["data"]["bus"]) == list

            bus_list = response_json["data"]["bus"]
            assert len(bus_list) > 0
            for bus_item in bus_list:
                assert "timetable" in bus_item.keys()
                timetable_list = bus_item["timetable"]
                assert type(timetable_list) == list
                assert len(timetable_list) >= 0
                for timetable_item in timetable_list:
                    assert "departureTime" in timetable_item.keys() and \
                           type(timetable_item["departureTime"]) == str


@pytest.mark.asyncio
async def test_bus_realtime_graphql():
    app_settings = AppSettings()
    with TestClient(app=app) as client:
        query = "query {" \
                "bus(stopList: [\"한양대게스트하우스\", \"한양대정문\"], " \
                "routes: [\"3102\", \"10-1\", \"707-1\"]){" \
                "realtime{lowFloor, remainedStop, remainedTime, remainedSeat}}}"
        response = client.post(f"{app_settings.API_V2_STR}", json={"query": query})
        response_json = response.json()
        assert response.status_code == 200
        assert "data" in response_json.keys()
        assert type(response_json["data"]) == dict

        assert "bus" in response_json["data"].keys()
        assert type(response_json["data"]["bus"]) == list

        bus_list = response_json["data"]["bus"]
        assert len(bus_list) > 0
        for bus_item in bus_list:
            assert "realtime" in bus_item.keys()
            realtime_list = bus_item["realtime"]
            assert type(realtime_list) == list
            assert len(realtime_list) >= 0
            for realtime_list_item in realtime_list:
                assert "lowFloor" in realtime_list_item.keys() and \
                       type(realtime_list_item["lowFloor"]) == bool
                assert "remainedStop" in realtime_list_item.keys() and \
                       type(realtime_list_item["remainedStop"]) == int
                assert "remainedTime" in realtime_list_item.keys() and \
                       type(realtime_list_item["remainedTime"]) == int
                assert "remainedSeat" in realtime_list_item.keys() and \
                       type(realtime_list_item["remainedSeat"]) == int


@pytest.mark.asyncio
async def test_reading_room_graphql():
    app_settings = AppSettings()
    campus_list = [0, 1]
    with TestClient(app=app) as client:
        for campus_id in campus_list:
            query = "query {" \
                    f"readingRoom(campusId: {campus_id}) " \
                    "{roomName, campusId, isActive, isReservable, totalSeat, activeSeat, " \
                    "occupiedSeat, availableSeat}}"
            response = client.post(f"{app_settings.API_V2_STR}", json={"query": query})
            response_json = response.json()
            assert response.status_code == 200
            assert "data" in response_json.keys()
            assert type(response_json["data"]) == dict
            assert "readingRoom" in response_json["data"].keys()
            assert type(response_json["data"]["readingRoom"]) == list

            reading_room_list = response_json["data"]["readingRoom"]
            assert len(reading_room_list) > 0
            for reading_room_item in reading_room_list:
                assert "roomName" in reading_room_item.keys() and \
                       type(reading_room_item["roomName"]) == str
                assert "campusId" in reading_room_item.keys() and \
                       type(reading_room_item["campusId"]) == int
                assert "isActive" in reading_room_item.keys() and \
                       type(reading_room_item["isActive"]) == bool
                assert "isReservable" in reading_room_item.keys() and \
                       type(reading_room_item["isReservable"]) == bool
                assert "totalSeat" in reading_room_item.keys() and \
                       type(reading_room_item["totalSeat"]) == int
                assert "activeSeat" in reading_room_item.keys() and \
                       type(reading_room_item["activeSeat"]) == int
                assert "occupiedSeat" in reading_room_item.keys() and \
                       type(reading_room_item["occupiedSeat"]) == int
                assert "availableSeat" in reading_room_item.keys() and \
                       type(reading_room_item["availableSeat"]) == int


@pytest.mark.asyncio
async def test_cafeteria_graphql():
    app_settings = AppSettings()
    campus_list = [0, 1]
    with TestClient(app=app) as client:
        for campus_id in campus_list:
            query = "query {" \
                    f"cafeteria(campusId: {campus_id}) " \
                    "{cafeteriaId, cafeteriaName, menu{timeType, menu, price}}}"
            response = client.post(f"{app_settings.API_V2_STR}", json={"query": query})
            response_json = response.json()
            assert response.status_code == 200
            assert "data" in response_json.keys()
            assert type(response_json["data"]) == dict
            assert "cafeteria" in response_json["data"].keys()
            assert type(response_json["data"]["cafeteria"]) == list

            cafeteria_list = response_json["data"]["cafeteria"]
            assert len(cafeteria_list) > 0
            for cafeteria_item in cafeteria_list:
                assert "cafeteriaId" in cafeteria_item.keys() and \
                       type(cafeteria_item["cafeteriaId"]) == int
                assert "cafeteriaName" in cafeteria_item.keys() and \
                       type(cafeteria_item["cafeteriaName"]) == str
                assert "menu" in cafeteria_item.keys() and \
                       type(cafeteria_item["menu"]) == list
                menu_list = cafeteria_item["menu"]
                for menu_item in menu_list:
                    assert "timeType" in menu_item.keys() and \
                           type(menu_item["timeType"]) == str
                    assert "menu" in menu_item.keys() and \
                           type(menu_item["menu"]) == str
                    assert "price" in menu_item.keys() and \
                           type(menu_item["price"]) == str
