from fastapi.testclient import TestClient
import slugify
from main import app
from pytest import fixture
from core.config import products

client = TestClient(app)


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


# @fixture(scope="session", autouse=True)
# def delete_products():
#     products.delete_many({"title": {"$in": ["тестовий товар", "тестовий товар2"]}})


# def test_product_list():
#     response = client.get("/products")
#     assert response.status_code == 200
#     assert len(response.json()) == 6


def test_product_retrieve():
    response = client.get("/products/testovii-tovar")
    assert response.status_code == 404
