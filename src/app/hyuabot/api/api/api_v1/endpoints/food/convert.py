from app.hyuabot.api.models.postgresql import cafeteria as db
from app.hyuabot.api.schemas.cafeteria import MenuItem


def convert_menu_item(menu_items: list[db.Menu]) -> dict[str, list[MenuItem]]:
    menu_dict: dict[str, list[MenuItem]] = {}
    for menu_item in menu_items:
        if menu_item.time_type not in menu_dict:
            menu_dict[menu_item.time_type] = []
        menu_dict[menu_item.time_type].append(
            MenuItem(name=menu_item.menu_description, price=menu_item.price))
    return menu_dict
