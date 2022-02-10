import asyncio

from fastapi import FastAPI

from app.hyuabot.api.initialize_data import load_shuttle_timetable

app = FastAPI()


def main():
    asyncio.run(load_shuttle_timetable())


main()
