import pytest as pytest
from httpx import AsyncClient

from app.hyuabot.api.core.config import AppSettings
from app.hyuabot.api.main import app

campus_keys = ["seoul", "erica"]
restaurant_keys = {
    "student_seoul": "학생식당",
    "life_science_seoul": "생활과학관 식당",
    "material_science_seoul": "신소재공학관 식당",
    "dorm_seoul_1": "제1생활관 식당",
    "dorm_seoul_2": "제2생활관 식당",
    "hangwon_seoul": "행원파크",
    "teacher_erica": "교직원식당",
    "student_erica": "학생식당",
    "dorm_erica": "창의인재원식당",
    "food_court_erica": "푸드코트",
    "changbo_erica": "창업보육센터"
}


@pytest.mark.asyncio
async def test_restaurant_menu_by_campus():
    app_settings = AppSettings()

    for campus_key in campus_keys:
        async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as client:
            response = await client.get(f"{app_settings.API_V1_STR}/food/campus"
                                        f"?campus={campus_key}")
            response_json = response.json()

            assert response.status_code == 200
            assert "campus" in response_json.keys() and type(response_json["campus"]) == str
            assert "restaurantList" in response_json.keys() and \
                   type(response_json["restaurantList"]) == list
            for restaurant in response_json["restaurantList"]:
                assert "name" in restaurant.keys() and type(restaurant["name"]) == str
                assert "workingTime" in restaurant.keys() and type(restaurant["workingTime"]) == str
                assert "menuList" in restaurant.keys() and type(restaurant["menuList"]) == dict
                for menu in restaurant["menuList"].values():
                    assert "menu" in menu.keys() and type(menu["menu"]) == str
                    assert "price" in menu.keys() and type(menu["price"]) == str


@pytest.mark.asyncio
async def test_restaurant_menu():
    app_settings = AppSettings()

    for restaurant_key, restaurant_name in restaurant_keys.items():
        async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as client:
            response = await client.get(f"{app_settings.API_V1_STR}/food?restaurant={restaurant_key}")
            response_json = response.json()

            assert response.status_code == 200
            assert "name" in response_json.keys() and type(response_json["name"]) == restaurant_name
            assert "workingTime" in response_json.keys() and type(response_json["workingTime"]) == str
            assert "menuList" in response_json.keys() and type(response_json["menuList"]) == dict
            for menu in response_json["menuList"].values():
                assert "menu" in menu.keys() and type(menu["menu"]) == str
                assert "price" in menu.keys() and type(menu["price"]) == str
