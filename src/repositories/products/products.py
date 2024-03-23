from bson import ObjectId
from fastapi import HTTPException
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError
from redis import Redis

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
            await products.find(
                filtering_data, {"_id": 0, "comments": 0, "available": 0, "stock": 0}
            )
            .sort({"created_at": 1})
            .to_list(None)
        )

    async def update_product(self, slug: str, updated_data: dict):
        updated_product = await products.find_one_and_update(
            {"slug": slug},
            updated_data,
            projection={"_id": 0, "title": 1, "description": 1},
            return_document=ReturnDocument.AFTER,
        )

        return updated_product

    async def delete_product(self, slug: str):
        return await products.delete_one({"slug": slug})

    async def add_comment(self, slug, comment: dict):
        try:
            update_product = await products.find_one_and_update(
                {"slug": slug},
                {"$push": {"comments": comment}},
                return_document=True,
                projection={"_id": 0, "comments": 1},
            )
            return update_product
        except:
            return {"error": "something went wrong"}

    # searching methods
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
            try:
                return await products.find(
                    filter_data, {"_id": 0, "comments": 0}
                ).to_list(None)
            except:
                raise HTTPException(500, "something went wrong")

        try:
            detail_product = await products.find_one(
                {"slug": slug}, {"_id": 0, "stock": 0, "available": 0, "created_at": 0}
            )
            rating = self.__get_avg_rating(detail_product, self.redis)

            detail_product["avg_rating"] = float(rating) if rating else 0

            return detail_product
        except Exception as e:
            raise HTTPException(500, f"{e}")

    async def category_by_title(self, title: list[str]) -> ObjectId | None:
        return await categories.find({"title": {"$in": title}}).to_list(None)

    @classmethod
    def __get_avg_rating(cls, product: dict, db: Redis) -> float | None:
        rating_key = f"rating:{product['slug']}"
        if db.get(rating_key) is None:

            if len(product["comments"]) == 0:
                return None

            summary_score = 0

            for comment in product["comments"]:
                summary_score += comment["score"]

            avg_rating = round(summary_score / len(product["comments"]), 2)

            db.set(rating_key, avg_rating, 86400)
            return avg_rating

        return db.get(f"rating:{product['slug']}")
