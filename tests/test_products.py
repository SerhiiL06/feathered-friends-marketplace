import pytest
from httpx import AsyncClient


@pytest.mark.asyncio(scope="session")
async def test_product_list(aclient: AsyncClient):
    response = await aclient.get("/products")
    assert response.status_code == 200
    assert len(response.json()) > 0

    response_with_params = await aclient.get(
        "/products",
        params={"tag": ["cats"]},
    )

    assert "cats" in response_with_params.json()[0]["tags"]


@pytest.mark.asyncio(scope="session")
async def test_product_retrieve(aclient: AsyncClient):
    wrong_response = await aclient.get("/products/testovii-tovar")
    correct_response = await aclient.get("/products/test-dlia-seleri5")
    assert wrong_response.status_code == 404
    assert wrong_response.json()["detail"] == {"message": "product dont found"}

    assert correct_response.status_code == 200
    assert bool(correct_response.json()["detail"]["slug"]) == True


@pytest.mark.asyncio(scope="session")
async def test_create_product(aclient: AsyncClient):
    fake_product_data = {
        "title": "test",
        "slug": "test",
        "description": "test",
        "brand": "test",
        "country": "test",
        "price": {"retail": 100, "wholesale": 50},
        "category_titles": ["test"],
        "stock": 4,
        "tags": ["test"],
    }
    response = await aclient.post(
        "/products",
        json=fake_product_data,
        headers={
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjVmYzJkMDgyNmI1N2RjNTk3YWQ5MTJmIiwiZW1haWwiOiJhZG1pbkBleGFtcGxlLmNvbSIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTcxMTU1ODYyN30.wqNa0NseD5Hhz9PrxGU2L2_dmGpU7WoggYuWDiot84I"
        },
    )
    assert response.status_code == 200


@pytest.mark.asyncio(scope="session")
async def test_update_product(aclient: AsyncClient):
    update_response = await aclient.patch(
        "/products/test",
        json={"title": "test1"},
        headers={
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjVmYzJkMDgyNmI1N2RjNTk3YWQ5MTJmIiwiZW1haWwiOiJhZG1pbkBleGFtcGxlLmNvbSIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTcxMTU1ODYyN30.wqNa0NseD5Hhz9PrxGU2L2_dmGpU7WoggYuWDiot84I"
        },
    )

    assert update_response.status_code == 200


@pytest.mark.asyncio(scope="session")
async def test_delete_product(aclient: AsyncClient):
    response = await aclient.delete("/products/test1")

    assert response.status_code == 200


@pytest.mark.asyncio(scope="session")
async def test_bookmark_action(aclient: AsyncClient):
    response = await aclient.post(
        "/products/test-dlia-seleri5/add-to-bookmark",
    )
    assert response.status_code == 200


@pytest.mark.asyncio(scope="session")
async def test_bookmark_list(aclient: AsyncClient):
    response = await aclient.get("/bookmarks")

    assert type(response.json()) == list
    assert len(response.json()) == 1
    assert response.json()[0]["slug"] == "test-dlia-seleri5"
