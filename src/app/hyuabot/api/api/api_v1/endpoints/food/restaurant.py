import json

from fastapi import APIRouter
from starlette.responses import JSONResponse

from app.hyuabot.api.api.api_v1.endpoints.reading_room import restaurant_query
from app.hyuabot.api.core.database import get_redis_connection, get_redis_value
from app.hyuabot.api.schemas.cafeteria import CafeteriaItem

restaurant_id_dict = {
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
    "changbo_erica": "창업보육센터",
}

restaurant_menu_router = APIRouter()


@restaurant_menu_router.get("/", status_code=200, response_model=CafeteriaItem)
async def fetch_restaurant(restaurant_id: str = restaurant_query):
    if restaurant_id in restaurant_id_dict.keys():
        redis_connection = await get_redis_connection("restaurant")
        json_string = await get_redis_value(redis_connection, restaurant_id)
        restaurant_item = json.loads(json_string.decode("utf-8"))
        await redis_connection.close()
        return {
            "name": restaurant_id_dict[restaurant_id], "workingTime": restaurant_item["time"],
            "menuList": restaurant_item["menu"],
        }
    return JSONResponse(status_code=404, content={"message": "Not Found"})
