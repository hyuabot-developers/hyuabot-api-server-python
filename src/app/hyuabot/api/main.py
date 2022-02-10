import asyncio

import hypercorn
from fastapi import FastAPI
from hypercorn import Config
from hypercorn.asyncio import serve

from app.hyuabot.api.api.api_v1.api import shuttle_router
from app.hyuabot.api.core.config import settings
from app.hyuabot.api.initialize_data import initialize_data

app = FastAPI()
app.include_router(shuttle_router, prefix=settings.API_V1_STR)


def main():
    initialize_data()

    config = Config()
    config.bind = ["localhost:8000"]

    asyncio.run(serve(app, config))


main()
