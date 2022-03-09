import ssl

import aiohttp
import certifi
from fastapi import APIRouter
import asyncio
import json

from bs4 import BeautifulSoup
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
    "changbo_erica": "15"
}


@fetch_restaurant_menu_router.get("", status_code=200)
async def fetch_reading_room() -> JSONResponse:
    tasks = []
    for restaurant_key, restaurant_url_key in restaurant_id_dict.items():
        tasks.append(fetch_restaurant_menu_by_id(restaurant_key, restaurant_url_key))
    await asyncio.gather(*tasks)
    return JSONResponse({"message": "Fetch restaurant menu data success"}, status_code=200)


async def fetch_restaurant_menu_by_id(restaurant_key: str, restaurant_url_key: str) -> None:
    url = f"https://www.hanyang.ac.kr/web/www/re{restaurant_url_key}"
    conn = aiohttp.TCPConnector(verify_ssl=False)

    async with aiohttp.ClientSession(connector=conn) as session:
        async with session.get(url) as response:
            cafeteria_info = {}
            soup = BeautifulSoup(await response.text(), "html.parser")

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
            for inbox in soup.find_all("div", {"class": "in-box"}):
                title = inbox.find("h4").text.strip()
                cafeteria_info[title] = []
                for list_item in inbox.find_all("li"):
                    if list_item.find("p", {"class": "price"}):
                        menu = list_item.find("h3").text.replace("\t", "").replace("\r\n", "")
                        p = list_item.find("h3").text
                        cafeteria_info[title].append({"menu": menu, "price": p})
            print(cafeteria_info)
            redis_connection = await get_redis_connection("restaurant")
            await set_redis_value(redis_connection, restaurant_key,
                                  json.dumps(cafeteria_info, ensure_ascii=False).encode("utf-8"))
            await redis_connection.close()
