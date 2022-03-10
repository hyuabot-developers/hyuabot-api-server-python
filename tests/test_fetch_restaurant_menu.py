import pytest
from httpx import AsyncClient

from app.hyuabot.api.main import app


@pytest.mark.asyncio
async def test_fetch_restaurant():
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as client:
        response = await client.get("/fetch/food")
        response_json = response.json()
        assert response.status_code == 200
        assert "message" in response_json.keys()
        assert "Fetch restaurant menu data success" == response_json["message"]
