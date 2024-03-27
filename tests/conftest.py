import pytest
import asyncio
from httpx import AsyncClient
from main import app


@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def aclient():
    async with AsyncClient(app=app, base_url="http://test") as aclient:
        yield aclient
