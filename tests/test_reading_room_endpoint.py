import pytest as pytest
from fastapi.testclient import TestClient


from app.hyuabot.api.core.config import AppSettings
from app.hyuabot.api.main import app


campus_keys = ["서울", "ERICA"]


@pytest.mark.asyncio
async def test_fetch_reading_room_information():
    with TestClient(app=app) as client:
        response = client.get("/fetch/library")
        response_json = response.json()
        assert response.status_code == 200
        assert "message" in response_json.keys()
        assert "Fetch reading room data success" == response_json["message"]


@pytest.mark.asyncio
async def test_reading_room_by_campus():
    app_settings = AppSettings()
    for campus in campus_keys:
        with TestClient(app=app) as client:
            response = client.get(f"{app_settings.API_V1_STR}/library/{campus}")
            response_json = response.json()

            assert response.status_code == 200
            assert type(response_json) == list
            for reading_room_item in response_json:
                assert "name" in reading_room_item.keys() and type(reading_room_item["name"] == str)
                assert "isActive" in reading_room_item.keys() and \
                       type(reading_room_item["isActive"]) == bool
                assert "isReservable" in reading_room_item.keys() and \
                       type(reading_room_item["isReservable"]) == bool
                assert "total" in reading_room_item.keys() and type(reading_room_item["total"]) == int
                assert "activeTotal" in reading_room_item.keys() and \
                       type(reading_room_item["activeTotal"]) == int
                assert "occupied" in reading_room_item.keys() and \
                    type(reading_room_item["occupied"]) == int
                assert "available" in reading_room_item.keys() and \
                       type(reading_room_item["available"]) == int
