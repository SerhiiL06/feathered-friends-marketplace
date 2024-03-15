from src.presentation.products.dto import ProductDTO
from src.repositories.products.products import ProductRepository
from dataclasses import asdict


class ProductDomain:
    def __init__(self) -> None:
        self.repo = ProductRepository()

    async def add_product(self, data: ProductDTO):

        new_object = await self.repo.create_product(asdict(data))

        return {"id": str(new_object.inserted_id)}

    async def all_products(self):
        return await self.repo.product_list()
