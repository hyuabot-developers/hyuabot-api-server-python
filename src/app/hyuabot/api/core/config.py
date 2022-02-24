import os

from pydantic import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    METRO_AUTH: str

    def __init__(self):
        super().__init__()
        if os.getenv("REDIS_HOST"):
            self.REDIS_HOST = os.getenv("REDIS_HOST")
        if os.getenv("REDIS_PORT") and os.getenv("REDIS_PORT").isdigit():
            self.REDIS_PORT = int(os.getenv("REDIS_PORT"))
        if os.getenv("METRO_AUTH"):
            self.METRO_AUTH = os.getenv("METRO_AUTH")
        else:
            raise ValueError("METRO_AUTH is not set")

settings = Settings()
