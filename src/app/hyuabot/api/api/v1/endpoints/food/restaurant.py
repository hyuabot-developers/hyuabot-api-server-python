from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.hyuabot.api.api.v1.endpoints.food.convert import convert_menu_item
from app.hyuabot.api.models.postgresql import cafeteria as db
from app.hyuabot.api.schemas.cafeteria import CafeteriaItem
from app.hyuabot.api.utlis.fastapi import get_db_session

restaurant_router = APIRouter(prefix="/restaurant")


@restaurant_router.get("/{cafeteria_id}", status_code=200, response_model=CafeteriaItem,
                       tags=["Cafeteria Menu"])
async def fetch_menu_by_cafeteria_id(cafeteria_id: str, db_session: Session = Depends(get_db_session)):
    cafeteria_item = db_session.query(db.Cafeteria)\
        .filter(db.Cafeteria.cafeteria_id == cafeteria_id).one_or_none()
    if cafeteria_item is None:
        return JSONResponse(status_code=404, content={"message": "존재하지 않는 식당입니다."})
    menu_items: list[db.Menu] = db_session.query(db.Menu)\
        .filter(db.Menu.cafeteria_id == cafeteria_id).all()
    return CafeteriaItem(
            name=cafeteria_item.cafeteria_name,
            workingTime="",
            menuList=convert_menu_item(menu_items),
    )
