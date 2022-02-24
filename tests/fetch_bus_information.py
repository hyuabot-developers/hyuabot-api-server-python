import pytest
from httpx import AsyncClient

from app.hyuabot.api.api.api_v1.endpoints.bus import bus_route_dict
from app.hyuabot.api.core.fetch.bus import fetch_bus_realtime
from app.hyuabot.api.main import app


@pytest.mark.asyncio
async def test_fetch_bus_information():
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as client:
        response = await client.get("/fetch/bus")
        response_json = response.json()
        assert response.status_code == 200
        assert "message" in response_json.keys()
        assert "Fetch bus data success" == response_json["message"]


@pytest.mark.asyncio
async def test_fetch_bus_information_realtime():
    for route_name, (route_id, station_id) in bus_route_dict.items():
        result = await fetch_bus_realtime(route_id, station_id)
        assert type(result) == list
        for realtime_item in result:
            assert "location" in realtime_item.keys()
            assert type(realtime_item["location"]) == int

            assert "lowPlate" in realtime_item.keys()
            assert type(realtime_item["lowPlate"]) == int

            assert "remainedTime" in realtime_item.keys()
            assert type(realtime_item["remainedTime"]) == int

            assert "remainedSeat" in realtime_item.keys()
            assert type(realtime_item["remainedSeat"]) == int
