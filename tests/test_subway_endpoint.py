import pytest as pytest
from httpx import AsyncClient

from app.hyuabot.api.main import app
from app.hyuabot.api.initialize_data import initialize_data
from app.hyuabot.api.core.config import AppSettings


campus_keys = ["erica"]


@pytest.mark.asyncio
async def test_subway_arrival():
    app_settings = AppSettings()
    await initialize_data()
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as client:
        for campus_key in campus_keys:
            response = await client.get(f"{app_settings.API_V1_STR}/subway/arrival/{campus_key}")
            response_json = response.json()

            assert response.status_code == 200
            assert "stationName" in response_json.keys() and type(response_json["stationName"]) == str
            assert "departureList" in response_json.keys() and \
                   type(response_json["departureList"]) == list

            for departure_info_item in response_json["departureList"]:
                assert "lineName" in departure_info_item.keys() and \
                       type(departure_info_item["lineName"]) == str
                assert "updateTime" in departure_info_item.keys() and \
                       type(departure_info_item["updateTime"]) == str
                assert "realtime" in departure_info_item.keys() and \
                       type(departure_info_item["realtime"]) == dict

                realtime_info = departure_info_item["realtime"]
                assert "up" in realtime_info.keys() and type(realtime_info["up"]) == list
                assert "down" in realtime_info.keys() and type(realtime_info["down"]) == list

                for heading_key in ["up", "down"]:
                    for realtime_item in realtime_info[heading_key]:
                        assert "terminalStation" in realtime_item.keys() and \
                               type(realtime_item["terminalStation"]) == str
                        assert "currentStation" in realtime_item.keys() and \
                               type(realtime_item["currentStation"]) == str
                        assert "statusCode" in realtime_item.keys() and \
                               type(realtime_item["statusCode"]) == str

                assert "timetable" in departure_info_item.keys() and \
                       type(departure_info_item["timetable"]) == dict
                timetable_info = departure_info_item["timetable"]
                assert "up" in timetable_info.keys() and type(timetable_info["up"]) == list
                assert "down" in timetable_info.keys() and type(timetable_info["down"]) == list

                for heading_key in ["up", "down"]:
                    for timetable_item in timetable_info[heading_key]:
                        assert "terminalStation" in timetable_item.keys() and \
                               type(timetable_item["terminalStation"]) == str
                        assert "departureTime" in timetable_item.keys() and \
                               type(timetable_item["departureTime"]) == str
