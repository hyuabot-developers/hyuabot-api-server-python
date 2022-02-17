import pytest as pytest
from httpx import AsyncClient

from app.hyuabot.api.api.api_v1.endpoints.shuttle import shuttle_line_type, shuttle_stop_type
from app.hyuabot.api.core.config import settings
from app.hyuabot.api.main import app


def check_shuttle_station_item(station_item: dict):
    assert "koreanName" in station_item.keys() and type(station_item["koreanName"]) == str
    assert "englishName" in station_item.keys() and type(station_item["englishName"]) == str
    assert "longitude" in station_item.keys() and type(station_item["longitude"]) == float
    assert "latitude" in station_item.keys() and type(station_item["latitude"]) == float


@pytest.mark.asyncio
async def test_shuttle_station_list():
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as client:
        for shuttle_type in shuttle_line_type:
            response = await client.get(f"{settings.API_V1_STR}/shuttle/route/station",
                                        params={"shuttleType": shuttle_type})
            response_json = response.json()

            assert response.status_code == 200
            assert "message" in response_json.keys() and type(response_json["message"]) == str

            assert "stationList" in response_json.keys() and type(response_json["stationList"]) == list
            for station_item in response_json["stationList"]:
                check_shuttle_station_item(station_item)


@pytest.mark.asyncio
async def test_shuttle_around_station():
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as client:
        response = await client.get(f"{settings.API_V1_STR}/shuttle/station/around",
                                    params={"latitude": 37.29246290291605,
                                            "longitude": 126.8359786509412})
        assert response.status_code == 200
        response_json = response.json()
        check_shuttle_station_item(response_json)


@pytest.mark.asyncio
async def test_shuttle_location():
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as client:
        for shuttle_type in shuttle_line_type:
            response = await client.get(f"{settings.API_V1_STR}/shuttle/location",
                                        params={"shuttleType": shuttle_type})
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
async def test_shuttle_arrival_list():
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as client:
        for shuttle_stop in shuttle_stop_type:
            response = await client.get(f"{settings.API_V1_STR}/shuttle/arrival/station",
                                        params={"shuttleStop": shuttle_stop})
            response_json = response.json()

            assert response.status_code == 200
            assert "busForStation" in response_json.keys() and type(
                response_json["busForStation"]) == list
            for shuttle_item in response_json["busForStation"]:
                assert "time" in shuttle_item.keys() and type(shuttle_item["time"]) == str
                assert "type" in shuttle_item.keys() and type(shuttle_item["type"]) == str
