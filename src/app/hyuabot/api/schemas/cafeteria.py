from pydantic import BaseModel, Field


class MenuItem(BaseModel):
    menu: str
    price: str


class CafeteriaItem(BaseModel):
    name: str
    working_time: str = Field(alias="workingTime")
    menu_list: dict[str, list[MenuItem]] = Field(alias="menuList")
