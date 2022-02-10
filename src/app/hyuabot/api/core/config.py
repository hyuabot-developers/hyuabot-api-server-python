import os

from pydantic import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    REDIS_HOST: str = os.getenv("REDIS_HOST") if os.getenv("REDIS_HOST") is not None else "localhost"
    REDIS_PORT: int = os.getenv("REDIS_PORT") \
        if os.getenv("REDIS_PORT") is not None and os.getenv("REDIS_PORT").isdigit() else 6379


settings = Settings()
