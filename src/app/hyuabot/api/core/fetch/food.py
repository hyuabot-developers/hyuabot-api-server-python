import asyncio
import json
from typing import Dict, Any, List

from bs4 import BeautifulSoup
from fastapi import APIRouter
from starlette.responses import JSONResponse

from app.hyuabot.api.core.database import get_redis_connection, set_redis_value

fetch_restaurant_menu_router = APIRouter(prefix="/food")
restaurant_id_dict = {
    "student_seoul": "1",
    "life_science_seoul": "2",
    "material_science_seoul": "4",
    "dorm_seoul_1": "6",
    "dorm_seoul_2": "7",
    "hangwon_seoul": "8",
    "teacher_erica": "11",
    "student_erica": "12",
    "dorm_erica": "13",
    "food_court_erica": "14",
    "changbo_erica": "15",
}


@fetch_restaurant_menu_router.get("", status_code=200)
async def fetch_reading_room() -> JSONResponse:
    from gevent import monkey
    monkey.patch_all()
    import grequests as grequests

    urls = []
    for restaurant_url_key in restaurant_id_dict.values():
        urls.append(f"https://www.hanyang.ac.kr/web/www/re{restaurant_url_key}")
    responses = [grequests.get(u) for u in urls]

    tasks = []
    for restaurant_key, response in zip(restaurant_id_dict.keys(), grequests.map(responses)):
        tasks.append(fetch_restaurant_menu_by_id(restaurant_key, response))
    await asyncio.gather(*tasks)
    return JSONResponse({"message": "Fetch restaurant menu data success"}, status_code=200)


async def fetch_restaurant_menu_by_id(restaurant_key: str, response) -> None:
    cafeteria_info: Dict[str, Any] = {}
    soup = BeautifulSoup(response.text, "html.parser")

    for inbox in soup.find_all("div", {"class": "tab-pane"}):
        for content in inbox.find_all("td"):
            txt = content.text.strip()
            cafeteria_info['time'] = ''
            if '조식' in txt:
                cafeteria_info['time'] += f'{txt}\n'
            elif '중식' in txt:
                cafeteria_info['time'] += f'{txt}\n'
            elif '석식' in txt:
                cafeteria_info['time'] += f'{txt}\n'
    cafeteria_info["menu"] = {}
    for inbox in soup.find_all("div", {"class": "in-box"}):
        title = inbox.find("h4").text.strip()
        cafeteria_info["menu"][title] = []
        for list_item in inbox.find_all("li"):
            if list_item.find("h3"):
                menu = list_item.find("h3").text.replace("\t", "").replace("\r\n", "")
                p = list_item.find("p", {"class": "price"}).text
                cafeteria_info["menu"][title].append({"menu": menu, "price": p})
    redis_connection = await get_redis_connection("restaurant")
    await set_redis_value(redis_connection, restaurant_key,
                          json.dumps(cafeteria_info, ensure_ascii=False).encode("utf-8"))
    await redis_connection.close()
