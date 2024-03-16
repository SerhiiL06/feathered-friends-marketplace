from core.config import products, categories
from bson import ObjectId


class ProductRepository:
    async def create_product(self, data: dict) -> dict:
        category_ids = await self.category_by_title(data.pop("category_titles"))

        cats = []

        for el in category_ids:
            cats.append({"id": str(el["_id"]), "title": el["title"]})

        data["category_ids"] = cats

        return await products.insert_one(data)

    async def product_list(self, filtering_data):

        return await products.find(filtering_data, {"_id": 0, "comments": 0}).to_list(
            None
        )

    async def product_by_slug(self, slug: str):
        return await products.find_one({"slug": slug})

    async def add_comment(self, slug, comment):
        return await products.find_one_and_update(
            {"slug": slug}, {"$push": {"comments": comment}}, return_document=True
        )

    async def category_by_title(self, title: list[str]) -> ObjectId | None:
        return await categories.find({"title": {"$in": title}}).to_list(None)

    async def delete_product(self, slug: str):
        return await products.delete_one({"slug": slug})