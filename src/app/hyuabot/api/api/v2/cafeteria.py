import strawberry
from sqlalchemy import and_
from sqlalchemy.orm import Session
from strawberry.types import Info

from app.hyuabot.api.models.postgresql.cafeteria import Menu


@strawberry.type
class MenuItem:
    time_type: str
    menu: str
    price: str


@strawberry.type
class CafeteriaItem:
    cafeteria_id: int
    cafeteria_name: str

    @strawberry.field
    def menu(self, info: Info, time_type: str | None) -> list[MenuItem]:
        db_session: Session = info.context["db_session"]
        expressions = [Menu.cafeteria_id == self.cafeteria_id]
        if time_type is not None:
            expressions.append(Menu.time_type == time_type)
        query = db_session.query(Menu).filter(and_(True, *expressions)).all()
        result: list[MenuItem] = []
        for x in query:  # type: Menu
            result.append(MenuItem(
                time_type=x.time_type,
                menu=x.menu_description,
                price=x.menu_price,
            ))
        return result
