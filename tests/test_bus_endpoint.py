import pytest as pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

from app.hyuabot.api import AppContext
from app.hyuabot.api.main import app
from app.hyuabot.api.initialize_data import initialize_data
from app.hyuabot.api.core.config import AppSettings


day_keys = ["weekdays", "saturday", "sunday"]
bus_route_keys = ["10-1", "707-1", "3102"]


@pytest.mark.asyncio
async def test_bus_arrival():
    app_settings = AppSettings()
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as client:
        db_session = Session(AppContext.from_app(app).db_engine)
        await initialize_data(db_session)

        response = await client.get(f"{app_settings.API_V1_STR}/bus/arrival")
        response_json = response.json()

        assert response.status_code == 200
        assert "departureInfoList" in response_json.keys() and \
               type(response_json["departureInfoList"]) == list

        for departure_info_item in response_json["departureInfoList"]:
            assert "message" in departure_info_item.keys() and \
                type(departure_info_item["message"]) == str
            assert "name" in departure_info_item.keys() and \
                type(departure_info_item["name"]) == str
            assert "busStop" in departure_info_item.keys() and \
                type(departure_info_item["busStop"]) == str
            assert "realtime" in departure_info_item.keys() and \
                type(departure_info_item["realtime"]) == list
            if departure_info_item["realtime"]:
                for realtime_item in departure_info_item["realtime"]:
                    assert "location" in realtime_item.keys() and \
                        type(realtime_item["location"]) == int
                    assert "lowPlate" in realtime_item.keys() and \
                        type(realtime_item["lowPlate"]) == int
                    assert "remainedTime" in realtime_item.keys() and \
                        type(realtime_item["remainedTime"]) == int
                    assert "remainedSeat" in realtime_item.keys() and \
                        type(realtime_item["remainedSeat"]) == int
            assert "timetable" in departure_info_item.keys() and \
                type(departure_info_item["timetable"]) == dict
            for day_key_item in day_keys:
                assert day_key_item in departure_info_item["timetable"].keys() and \
                    type(departure_info_item["timetable"][day_key_item]) == list
                for timetable_item in departure_info_item["timetable"][day_key_item]:
                    assert len(timetable_item.split(":")) == 3
                    hour, minute, second = timetable_item.split(":")
                    assert 0 <= int(hour) <= 23
                    assert 0 <= int(minute) <= 59
                    assert 0 <= int(second) <= 59
        db_session.close()


@pytest.mark.asyncio
async def test_bus_arrival_by_route():
    app_settings = AppSettings()
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as client:
        db_session = Session(AppContext.from_app(app).db_engine)
        await initialize_data(db_session)
        for bus_route in bus_route_keys:
            response = await client.get(f"{app_settings.API_V1_STR}/bus/arrival/route/{bus_route}",
                                        params={"count": 2})
            response_json = response.json()

            assert response.status_code == 200
            assert "message" in response_json.keys() and \
                   type(response_json["message"]) == str
            assert "name" in response_json.keys() and \
                   type(response_json["name"]) == str
            assert "busStop" in response_json.keys() and \
                   type(response_json["busStop"]) == str
            assert "realtime" in response_json.keys() and \
                   type(response_json["realtime"]) == list
            if response_json["realtime"]:
                for realtime_item in response_json["realtime"]:
                    assert "location" in realtime_item.keys() and \
                           type(realtime_item["location"]) == int
                    assert "lowPlate" in realtime_item.keys() and \
                           type(realtime_item["lowPlate"]) == int
                    assert "remainedTime" in realtime_item.keys() and \
                           type(realtime_item["remainedTime"]) == int
                    assert "remainedSeat" in realtime_item.keys() and \
                           type(realtime_item["remainedSeat"]) == int
            assert "timetable" in response_json.keys() and \
                   type(response_json["timetable"]) == dict
            for day_key_item in day_keys:
                assert day_key_item in response_json["timetable"].keys() and \
                       type(response_json["timetable"][day_key_item]) == list and \
                       len(response_json["timetable"][day_key_item]) == 2
                for timetable_item in response_json["timetable"][day_key_item]:
                    assert len(timetable_item.split(":")) == 3
                    hour, minute, second = timetable_item.split(":")
                    assert 0 <= int(hour) <= 23
                    assert 0 <= int(minute) <= 59
                    assert 0 <= int(second) <= 59
        db_session.close()


@pytest.mark.asyncio
async def test_bus_timetable():
    app_settings = AppSettings()
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as client:
        db_session = Session(AppContext.from_app(app).db_engine)
        await initialize_data(db_session)
        for bus_route in bus_route_keys:
            response = await client.get(f"{app_settings.API_V1_STR}/bus/timetable/{bus_route}",
                                        params={"count": 2})
            response_json = response.json()
            for day_key_item in day_keys:
                assert day_key_item in response_json.keys() and \
                       type(response_json[day_key_item]) == list
                for timetable_item in response_json[day_key_item]:
                    assert len(timetable_item.split(":")) == 3
                    hour, minute, second = timetable_item.split(":")
                    assert 0 <= int(hour) <= 23
                    assert 0 <= int(minute) <= 59
                    assert 0 <= int(second) <= 59
        db_session.close()
