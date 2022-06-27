from fastapi.testclient import TestClient
import pytest as pytest

from app.hyuabot.api import AppSettings
from app.hyuabot.api.api.v1.endpoints.shuttle import shuttle_line_type, shuttle_stop_type
from app.hyuabot.api.main import app


def check_shuttle_station_item(station_item: dict):
    assert "koreanName" in station_item.keys() and type(station_item["koreanName"]) == str
    assert "englishName" in station_item.keys() and type(station_item["englishName"]) == str
    assert "longitude" in station_item.keys() and type(station_item["longitude"]) == float
    assert "latitude" in station_item.keys() and type(station_item["latitude"]) == float


@pytest.mark.asyncio
async def test_shuttle_station_list():
    app_settings = AppSettings()

    with TestClient(app=app) as app_client:
        for shuttle_type in shuttle_line_type:
            url = f"{app_settings.API_V1_STR}/shuttle/route/station/{shuttle_type}"
            response = app_client.get(url)
            response_json = response.json()

            assert response.status_code == 200
            assert "message" in response_json.keys() and type(response_json["message"]) == str

            assert "stationList" in response_json.keys() and type(response_json["stationList"]) == list
            for station_item in response_json["stationList"]:
                check_shuttle_station_item(station_item)


@pytest.mark.asyncio
async def test_shuttle_around_station():
    app_settings = AppSettings()
    with TestClient(app=app) as app_client:
        response = app_client.get(f"{app_settings.API_V1_STR}/shuttle/station/around",
                                  params={"latitude": 37.29246290291605,
                                          "longitude": 126.8359786509412})
        assert response.status_code == 200
        response_json = response.json()
        check_shuttle_station_item(response_json)


@pytest.mark.asyncio
async def test_shuttle_location():
    app_settings = AppSettings()
    with TestClient(app=app) as app_client:
        for shuttle_type in shuttle_line_type:
            response = app_client.get(f"{app_settings.API_V1_STR}/shuttle/location/{shuttle_type}")
            assert response.status_code == 200
            response_json = response.json()

            assert "message" in response_json.keys() and type(response_json["message"]) == str
            assert "shuttleList" in response_json.keys() and type(response_json["shuttleList"]) == list
            for shuttle_item in response_json["shuttleList"]:
                assert "currentStation" in shuttle_item.keys() and \
                       type(shuttle_item["currentStation"]) == str
                assert "currentStationSeq" in shuttle_item.keys() and \
                       type(shuttle_item["currentStationSeq"]) == int
                assert "lastShuttle" in shuttle_item.keys() and \
                       type(shuttle_item["lastShuttle"]) == bool


@pytest.mark.asyncio
async def test_shuttle_arrival_list_in_a_row():
    app_settings = AppSettings()
    with TestClient(app=app) as app_client:
        url = f"{app_settings.API_V1_STR}/shuttle/arrival"
        response = app_client.get(url)
        response_json = response.json()

        assert response.status_code == 200
        assert "arrivalList" in response_json.keys() and type(response_json["arrivalList"]) == list
        for stop_item in response_json["arrivalList"]:
            assert "stopName" in stop_item.keys() and type(stop_item["stopName"]) == str
            assert "busForStation" in stop_item.keys() and type(
                stop_item["busForStation"]) == list
            for shuttle_item in stop_item["busForStation"]:
                assert "time" in shuttle_item.keys() and type(shuttle_item["time"]) == str
                assert "type" in shuttle_item.keys() and type(shuttle_item["type"]) == str
            assert "busForTerminal" in stop_item.keys() and type(
                stop_item["busForTerminal"]) == list
            for shuttle_item in stop_item["busForTerminal"]:
                assert "time" in shuttle_item.keys() and type(shuttle_item["time"]) == str
                assert "type" in shuttle_item.keys() and type(shuttle_item["type"]) == str


@pytest.mark.asyncio
async def test_shuttle_arrival_list():
    app_settings = AppSettings()
    with TestClient(app=app) as app_client:
        for shuttle_stop in shuttle_stop_type:
            url = f"{app_settings.API_V1_STR}/shuttle/arrival/{shuttle_stop}"
            response = app_client.get(url)
            response_json = response.json()

            assert response.status_code == 200
            assert "stopName" in response_json.keys() and type(response_json["stopName"]) == str
            assert "busForStation" in response_json.keys() and type(
                response_json["busForStation"]) == list
            for shuttle_item in response_json["busForStation"]:
                assert "time" in shuttle_item.keys() and type(shuttle_item["time"]) == str
                assert "type" in shuttle_item.keys() and type(shuttle_item["type"]) == str
            assert "busForTerminal" in response_json.keys() and type(
                response_json["busForTerminal"]) == list
            for shuttle_item in response_json["busForTerminal"]:
                assert "time" in shuttle_item.keys() and type(shuttle_item["time"]) == str
                assert "type" in shuttle_item.keys() and type(shuttle_item["type"]) == str


@pytest.mark.asyncio
async def test_shuttle_timetable_list():
    app_settings = AppSettings()
    with TestClient(app=app) as app_client:
        for shuttle_stop in shuttle_stop_type:
            url = f"{app_settings.API_V1_STR}/shuttle/arrival/{shuttle_stop}/timetable"
            response = app_client.get(url)
            response_json = response.json()

            assert response.status_code == 200
            assert "stopName" in response_json.keys() and type(response_json["stopName"]) == str
            assert "busForStation" in response_json.keys() and type(
                response_json["busForStation"]) == list
            for shuttle_item in response_json["busForStation"]:
                assert "time" in shuttle_item.keys() and type(shuttle_item["time"]) == str
                assert "type" in shuttle_item.keys() and type(shuttle_item["type"]) == str
            assert "busForTerminal" in response_json.keys() and type(
                response_json["busForTerminal"]) == list
            for shuttle_item in response_json["busForTerminal"]:
                assert "time" in shuttle_item.keys() and type(shuttle_item["time"]) == str
                assert "type" in shuttle_item.keys() and type(shuttle_item["type"]) == str
