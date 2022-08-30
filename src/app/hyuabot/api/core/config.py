import os
from typing import Dict, Any

from pydantic import AnyUrl, BaseSettings, Field


class AppSettings(BaseSettings):
    API_V1_STR: str = Field(default="/api/v1")
    API_V2_STR: str = Field(default="/api/v2")
    DATABASE_URI: AnyUrl = Field(
        default=f"postgresql://{os.environ.get('POSTGRES_USER', 'postgres')}:"
                f"{os.environ.get('POSTGRES_PASSWORD', 'postgres')}@"
                f"{os.environ.get('POSTGRES_HOST', 'localhost')}:"
                f"{os.environ.get('POSTGRES_PORT', 5432)}/hyuabot")
    BUS_API_KEY = Field(default=os.environ.get("BUS_API_KEY", "1234567890"))
    METRO_API_KEY = Field(default=os.environ.get("METRO_API_KEY", "sample"))
    DATABASE_OPTIONS: Dict[str, Any] = Field(
        default={
            'connect_args': {
                'keepalives': 1,
                'keepalives_idle': 30,
                'keepalives_interval': 15,
            },
            'pool_pre_ping': True,
            'pool_recycle': 15 * 60,
            'pool_size': 50,
            'max_overflow': 50,
            'pool_use_lifo': True,
        },
        description='PosstgreSQL option to create a connection.',
    )
