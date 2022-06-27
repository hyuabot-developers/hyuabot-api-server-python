from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.hyuabot.api.api.v1.endpoints.food.convert import convert_menu_item
from app.hyuabot.api.models.postgresql.cafeteria import Cafeteria, Menu
from app.hyuabot.api.models.postgresql.campus import Campus
from app.hyuabot.api.schemas.cafeteria import CampusItem, CafeteriaItem
from app.hyuabot.api.utlis.fastapi import get_db_session

restaurant_menu_campus_router = APIRouter(prefix="/campus")


@restaurant_menu_campus_router.get("/{campus_name}", status_code=200,
                                   response_model=CampusItem, tags=["Restaurant Menu By campus"])
async def fetch_restaurant_by_campus(campus_name: str, db_session: Session = Depends(get_db_session)):
    campus_item = db_session.query(Campus).filter(Campus.campus_name == campus_name).one_or_none()
    if campus_item is None:
        return JSONResponse(status_code=404, content={"message": "존재하지 않는 캠퍼스입니다."})
    cafeteria_items: list[Cafeteria] = db_session.query(Cafeteria)\
        .filter(Cafeteria.campus_id == campus_item.campus_id).all()
    menu_items: list[Menu] = db_session.query(Menu).all()
    cafeteria_list = []
    for cafeteria_item in cafeteria_items:
        menu_items_cafeteria = convert_menu_item(
            list(filter(lambda x: x.cafeteria_id == cafeteria_item.cafeteria_id, menu_items)))
        cafeteria_list.append(CafeteriaItem(
            name=cafeteria_item.cafeteria_name,
            workingTime="",
            menuList=menu_items_cafeteria,
        ))

    return {"campus": campus_name, "restaurantList": cafeteria_list}
