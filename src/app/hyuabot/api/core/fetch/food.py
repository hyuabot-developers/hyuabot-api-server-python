import asyncio
from typing import Dict, Any

import requests
from bs4 import BeautifulSoup
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.hyuabot.api.models.postgresql.cafeteria import Menu, Cafeteria
from app.hyuabot.api.utlis.fastapi import get_db_session

fetch_restaurant_menu_router = APIRouter(prefix="/food")


@fetch_restaurant_menu_router.get("", status_code=200)
async def fetch_restaurant_menu(db_session: Session = Depends(get_db_session)) -> JSONResponse:
    cafeteria_id_list = db_session.query(Cafeteria.cafeteria_id).distinct().all()
    urls = []
    for (restaurant_url_key,) in cafeteria_id_list:
        print(f"https://www.hanyang.ac.kr/web/www/re{restaurant_url_key}")
        urls.append(f"https://www.hanyang.ac.kr/web/www/re{restaurant_url_key}")
    responses = [requests.get(u) for u in urls]
    db_session.query(Menu).delete()
    tasks = []
    for (restaurant_key,), response in zip(cafeteria_id_list, responses):
        tasks.append(fetch_restaurant_menu_by_id(db_session, restaurant_key, response))
    await asyncio.gather(*tasks)
    return JSONResponse({"message": "Fetch restaurant menu data success"}, status_code=200)


async def fetch_restaurant_menu_by_id(db_session: Session, cafeteria_id: str, response) -> None:
    menu_list = []
    print(response)
    soup = BeautifulSoup(response.text, "html.parser")
    for inbox in soup.find_all("div", {"class": "in-box"}):
        title = inbox.find("h4").text.strip()
        for list_item in inbox.find_all("li"):
            if list_item.find("h3"):
                menu = list_item.find("h3").text.replace("\t", "").replace("\r\n", "")
                p = list_item.find("p", {"class": "price"}).text
                menu_list.append(Menu(
                    cafeteria_id=cafeteria_id,
                    time_type=title,
                    menu_description=menu,
                    menu_price=p
                ))
    db_session.add_all(menu_list)
    db_session.commit()

