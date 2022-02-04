from pydantic.main import BaseModel


class MenuItem(BaseModel):
    menu: str
    price: str


class CafeteriaItem(BaseModel):
    name: str
    workingTime: str
    menuList: dict[str, list[MenuItem]]
