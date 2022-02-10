from fastapi import FastAPI

from app.hyuabot.api.initialize_data import initialize_data

app = FastAPI()


def main():
    initialize_data()


main()
