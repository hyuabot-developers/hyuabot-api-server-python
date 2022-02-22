from fastapi import FastAPI

from app.hyuabot.api.api.api_v1.api import shuttle_router, bus_router
from app.hyuabot.api.api.fetch import fetch_router
from app.hyuabot.api.core.config import settings
from app.hyuabot.api.initialize_data import initialize_data

app = FastAPI()


@app.on_event("startup")
async def startup():
    await initialize_data()


app.include_router(shuttle_router, prefix=settings.API_V1_STR)
app.include_router(bus_router, prefix=settings.API_V1_STR)
app.include_router(fetch_router)
