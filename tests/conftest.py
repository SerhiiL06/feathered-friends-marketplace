import asyncio

import pytest
from httpx import ASGITransport, AsyncClient

from core.config import products, redis_client
from main import app


@pytest.fixture(scope="session", autouse=True)
async def clear_fake_data():
    print("start")
    yield
    redis_client.delete("bookmark:fakecookie")


@pytest.fixture(scope="session")
async def aclient():
    async with ASGITransport(app=app) as tran:
        aclient = AsyncClient(
            transport=tran,
            base_url="http://test",
            cookies={"session_key": "fakecookie"},
        )
        yield aclient
