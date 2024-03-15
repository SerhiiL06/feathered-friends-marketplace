from core.config import products, categories
from bson import ObjectId


class ProductRepository:
    async def create_product(self, data: dict) -> dict:
        category_ids = await self.category_by_title(data.pop("category_titles"))

        cats = []

        for el in category_ids:
            cats.append(el["_id"])
        data["category_ids"] = cats

        return await products.insert_one(data)

    async def product_list(self, filters: dict = None):
        return await products.find({}, {"_id": 0}).to_list(None)

    async def category_by_title(self, title: list[str]) -> ObjectId | None:
        return await categories.find({"title": {"$in": title}}, {"_id": 1}).to_list(
            None
        )
