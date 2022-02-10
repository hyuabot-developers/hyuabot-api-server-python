from pydantic import BaseModel, Field


class MenuItem(BaseModel):
    menu: str = Field(alias="menu", title="메뉴", description="식단")
    price: str = Field(alias="price", title="가격", description="메뉴별 가격")


class CafeteriaItem(BaseModel):
    name: str = Field(alias="name", title="이름", description="식당 이름")
    working_time: str = Field(alias="workingTime", title="운영 시간", description="예시: 09:00 ~ 21:00")
    menu_list: dict[str, list[MenuItem]] = Field(alias="menuList", title="메뉴 목록", description="식단 목록")
