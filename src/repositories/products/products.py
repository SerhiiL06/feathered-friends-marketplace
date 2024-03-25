from bson import ObjectId
from fastapi import HTTPException
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError


from core.config import RedisTools, categories, comments, products


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

    # comment methods
    async def create_comment(self, comment: dict):
        try:
            new = await comments.insert_one(comment)
            return {"comment": str(new.inserted_id)}

        except:
            return {"error": "something went wrong"}

    async def get_user_comments(self, user_id):
        try:
            return await comments.find({"user_id": user_id}, {"_id": 0}).to_list(None)
        except:
            return "error"

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

        detail_product = await products.find_one(
            {"slug": slug}, {"_id": 0, "stock": 0, "available": 0, "created_at": 0}
        )

        return detail_product
        # except Exception as e:
        #     raise HTTPException(500, f"{e.with_traceback()}")

    async def category_by_title(self, title: list[str]) -> ObjectId | None:
        return await categories.find({"title": {"$in": title}}).to_list(None)

    async def get_comment_by_post(self, slug):
        list_of_comment = await comments.find({"product": slug}, {"_id": 0}).to_list(
            None
        )
        return list_of_comment

    def get_avg_rating(self, product: dict) -> float | None:
        rating_key = f"rating:{product['slug']}"
        if self.redis.get(rating_key) is None:

            if product.get("comments") is None:
                return None

            summary_score = 0

            for comment in product["comments"]:
                summary_score += comment["score"]

            avg_rating = round(summary_score / len(product["comments"]), 2)

            self.redis.set(rating_key, avg_rating, 86400)
            return avg_rating

        return self.redis.get(f"rating:{product['slug']}")
