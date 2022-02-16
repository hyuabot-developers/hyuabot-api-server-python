from fastapi.testclient import TestClient

from app.hyuabot.api.api.api_v1.endpoints.shuttle import shuttle_line_type, shuttle_stop_type
from app.hyuabot.api.core.config import settings
from app.hyuabot.api.main import app

client = TestClient(app)


def check_shuttle_station_item(station_item: dict):
    assert "koreanName" in station_item.keys() and type(station_item["koreanName"]) == str
    assert "englishName" in station_item.keys() and type(station_item["englishName"]) == str
    assert "longitude" in station_item.keys() and type(station_item["longitude"]) == float
    assert "latitude" in station_item.keys() and type(station_item["latitude"]) == float


def test_shuttle_station_list_endpoint():
    for shuttle_type in shuttle_line_type:
        response = client.get(f"{settings.API_V1_STR}/shuttle/route/station",
                              params={"shuttleType": shuttle_type})
        response_json = response.json()

        assert response.status_code == 200
        assert "message" in response_json.keys() and type(response_json["message"]) == str

        assert "stationList" in response_json.keys() and type(response_json["stationList"]) == list
        for station_item in response_json["stationList"]:
            check_shuttle_station_item(station_item)


def test_shuttle_around_station():
    response = client.get(f"{settings.API_V1_STR}/shuttle/station/around",
                          params={"latitude": 37.29246290291605, "longitude": 126.8359786509412})
    response_json = response.json()

    assert response.status_code == 200
    check_shuttle_station_item(response_json)


def test_shuttle_location():
    for shuttle_type in shuttle_line_type:
        response = client.get(f"{settings.API_V1_STR}/shuttle/location",
                              params={"shuttleType": shuttle_type})
        response_json = response.json()

        assert response.status_code == 200
        assert "message" in response_json.keys() and type(response_json["message"]) == str
        assert "shuttleList" in response_json.keys() and type(response_json["shuttleList"]) == list
        for shuttle_item in response_json["shuttleList"]:
            assert "currentStation" in shuttle_item.keys() and \
                   type(shuttle_item["currentStation"]) == str
            assert "currentStationSeq" in shuttle_item.keys() and \
                   type(shuttle_item["currentStationSeq"]) == int
            assert "lastShuttle" in shuttle_item.keys() and \
                   type(shuttle_item["lastShuttle"]) == bool


def test_shuttle_arrival_list():
    for shuttle_stop in shuttle_stop_type:
        response = client.get(f"{settings.API_V1_STR}/shuttle/arrival/station",
                              params={"shuttleStop": shuttle_stop})
        response_json = response.json()

        assert response.status_code == 200
        assert "busForStation" in response_json.keys() and type(response_json["busForStation"]) == list
        for shuttle_item in response_json["busForStation"]:
            assert "time" in shuttle_item.keys() and type(shuttle_item["time"]) == str
            assert "type" in shuttle_item.keys() and type(shuttle_item["type"]) == str
