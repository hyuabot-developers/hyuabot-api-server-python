import os

from pydantic import AnyUrl, BaseSettings, Field


class AppSettings(BaseSettings):
    API_V1_STR: str = Field(default="/api/v1")
    REDIS_URI: AnyUrl = Field(
        default=f"redis://{os.environ.get('REDIS_HOST', 'localhost')}:"
                f"{os.environ.get('REDIS_PORT', 6379)}")
    BUS_API_KEY = Field(default=os.environ.get('BUS_API_KEY', '1234567890'))
