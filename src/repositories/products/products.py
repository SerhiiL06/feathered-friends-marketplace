from bson import ObjectId
from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError

from core.config import RedisTools, categories, products


class ProductRepository:
    def __init__(self) -> None:
        client = RedisTools()
        self.redis = client.connect_redis

    async def create_product(self, data: dict) -> dict:
        category_ids = await self.category_by_title(data.pop("category_titles"))

        cats = []

        for el in category_ids:
            cats.append({"id": str(el["_id"]), "title": el["title"]})

        data["category_ids"] = cats
        try:
            return await products.insert_one(data)
        except DuplicateKeyError:
            raise HTTPException(400, {"error": "product with this slug already exists"})

    async def product_list(self, filtering_data: dict, available: bool = True):
        if available:
            filtering_data.update({"stock": {"$gt": 0}})
        return (
            await products.find(filtering_data, {"_id": 0, "comments": 0})
            .sort({"created_at": 1})
            .to_list(None)
        )

    async def product_by_ids(self, ids: int | list):
        if isinstance(ids, list):
            ids = list(map(lambda x: ObjectId(x), ids))
            product_list = await products.find(
                {"_id": {"$in": ids}}, {"comments": 0}
            ).to_list(None)
            return product_list
        return await products.find_one({"_id": ids})

    async def product_by_slug(self, slug: str | set) -> list | dict:

        if isinstance(slug, set):
            list_of_slugs = list(map(lambda x: x.decode("utf-8"), slug))
            filter_data = {"slug": {"$in": list_of_slugs}}

            return await products.find(filter_data, {"_id": 0, "comments": 0}).to_list(
                None
            )
        detail_product = await products.find_one(
            {"slug": slug}, {"_id": 0, "stock": 0, "available": 0, "created_at": 0}
        )

        detail_product["avg_rating"] = self.get_avg_rating(slug)
        return detail_product

    async def add_comment(self, slug, comment: dict):
        try:
            update_product = await products.find_one_and_update(
                {"slug": slug},
                {"$push": {"comments": comment}},
                return_document=True,
                projection={"_id": 0, "comments": 1},
            )
            pip = self.redis.pipeline()
            pip.incrby(f"score:count:{slug}")
            pip.incrby(f"score:summary:{slug}", comment["score"])
            pip.execute()
            return update_product
        except:
            return {"error": "something went wrong"}

    async def category_by_title(self, title: list[str]) -> ObjectId | None:
        return await categories.find({"title": {"$in": title}}).to_list(None)

    async def delete_product(self, slug: str):
        return await products.delete_one({"slug": slug})

    def get_avg_rating(self, slug: str) -> float:
        avg_key = f"score:avg:{slug}"
        count_key = f"score:count:{slug}"
        summary_key = f"score:summary:{slug}"
        if not self.redis.get(avg_key):
            if self.redis.get(summary_key) is None or self.redis.get(count_key) is None:
                return None
            avg = int(self.redis.get(summary_key)) / int(self.redis.get(count_key))
            self.redis.set(avg_key, avg, 3600)
            return avg
        return self.redis.get(avg_key)
