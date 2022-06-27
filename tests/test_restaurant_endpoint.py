import pytest as pytest
from fastapi.testclient import TestClient

from app.hyuabot.api.core.config import AppSettings
from app.hyuabot.api.main import app

campus_keys = ["서울", "ERICA"]
restaurant_keys = {
    "1": "학생식당",
    "2": "생활과학관 식당",
    "4": "신소재공학관 식당",
    "6": "제1생활관식당",
    "7": "제2생활관식당",
    "8": "행원파크",
    "11": "교직원식당",
    "12": "학생식당",
    "13": "창의인재원식당",
    "14": "푸드코트",
    "15": "창업보육센터",
}


@pytest.mark.asyncio
async def test_restaurant_menu_by_campus():
    app_settings = AppSettings()

    for campus_key in campus_keys:
        with TestClient(app=app) as client:
            response = client.get(f"{app_settings.API_V1_STR}/food/campus/{campus_key}")
            response_json = response.json()

            assert response.status_code == 200
            assert "campus" in response_json.keys() and type(response_json["campus"]) == str
            assert "restaurantList" in response_json.keys() and \
                   type(response_json["restaurantList"]) == list
            for restaurant in response_json["restaurantList"]:
                assert "name" in restaurant.keys() and type(restaurant["name"]) == str
                assert "workingTime" in restaurant.keys() and type(restaurant["workingTime"]) == str
                assert "menuList" in restaurant.keys() and type(restaurant["menuList"]) == dict
                for menu_list in restaurant["menuList"].values():
                    for menu in menu_list:
                        assert "menu" in menu.keys() and type(menu["menu"]) == str
                        assert "price" in menu.keys() and type(menu["price"]) == str


@pytest.mark.asyncio
async def test_restaurant_menu():
    app_settings = AppSettings()

    for restaurant_key, restaurant_name in restaurant_keys.items():
        with TestClient(app=app) as client:
            response = client.get(f"{app_settings.API_V1_STR}/food/restaurant/{restaurant_key}")
            response_json = response.json()

            assert response.status_code == 200
            assert "name" in response_json.keys() and response_json["name"] == restaurant_name
            assert "workingTime" in response_json.keys() and type(response_json["workingTime"]) == str
            assert "menuList" in response_json.keys() and type(response_json["menuList"]) == dict
            for menu_list in response_json["menuList"].values():
                for menu in menu_list:
                    assert "menu" in menu.keys() and type(menu["menu"]) == str
                    assert "price" in menu.keys() and type(menu["price"]) == str
