from .api import shuttle_router, bus_router, subway_router
from .endpoints.food import restaurant_menu_router
from .endpoints.reading_room.campus import reading_room_router

__all__ = ['API_V1_ROUTERS']

API_V1_ROUTERS = [shuttle_router, bus_router, reading_room_router, restaurant_menu_router, subway_router]
