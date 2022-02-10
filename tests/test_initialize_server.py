import asyncio
import json

import aioredis
import pytest

from app.hyuabot.api.core.config import settings
from app.hyuabot.api.initialize_data import load_shuttle_timetable


@pytest.mark.asyncio
async def test_store_shuttle_timetable():
    await load_shuttle_timetable()

    term_keys = ["semester", "vacation", "vacation_session"]
    day_keys = ["week", "weekend"]
    redis_client = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}")

    async with redis_client.client() as connection:
        for term in term_keys:
            for day in day_keys:
                key = f"shuttle_{term}_{day}"
                json_string: bytes = await connection.get(key)
                timetable: list[dict] = json.loads(json_string.decode("utf-8"))

                assert len(timetable) > 0
                for shuttle_time in timetable:
                    assert "time" in shuttle_time.keys()
                    assert "type" in shuttle_time.keys()
