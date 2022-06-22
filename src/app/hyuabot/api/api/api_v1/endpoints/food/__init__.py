# Query params
from fastapi import APIRouter

from app.hyuabot.api.api.api_v1.endpoints.food.campus import restaurant_menu_campus_router
from app.hyuabot.api.api.api_v1.endpoints.food.restaurant import restaurant_router

restaurant_menu_router = APIRouter(prefix="/food")
restaurant_menu_router.include_router(restaurant_menu_campus_router)
restaurant_menu_router.include_router(restaurant_router)
