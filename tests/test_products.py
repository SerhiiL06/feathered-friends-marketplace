import slugify
from pytest import fixture
from core.config import products
from httpx import AsyncClient


@fixture(scope="session")
def create_product():
    product1 = {
        "title": "тестовий товар",
        "description": "this product for testing",
        "price": {"retail": 100, "wholesale": 50},
        "tags": ["test"],
    }
    product2 = {
        "title": "тестовий товар2",
        "description": "this product for testing2",
        "price": {"retail": 100, "wholesale": 50},
        "tags": ["test2"],
    }
    product1["slug"] = slugify.slugify(product1["title"])
    product2["slug"] = slugify.slugify(product2["title"])
    products.insert_many([product1, product2])


async def test_product_list(aclient: AsyncClient):
    response = await aclient.get("/products")
    assert response.status_code == 200
    assert len(response.json()) > 0


async def test_product_retrieve(aclient: AsyncClient):
    wrong_response = await aclient.get("/products/testovii-tovar")
    correct_response = await aclient.get("/products/test-dlia-seleri5")
    assert wrong_response.status_code == 404
    assert wrong_response.json() == {"detail": {"message": "product dont found"}}

    assert correct_response.status_code == 200
    assert bool(correct_response.json()["detail"]["comments"]) == False
