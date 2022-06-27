import pytest
from fastapi.testclient import TestClient

from app.hyuabot.api.main import app


@pytest.mark.asyncio
async def test_fetch_restaurant():
    with TestClient(app=app) as client:
        response = client.get("/fetch/food")
        response_json = response.json()
        assert response.status_code == 200
        assert "message" in response_json.keys()
        assert "Fetch restaurant menu data success" == response_json["message"]
