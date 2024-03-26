from fastapi import Response, HTTPException
from dataclasses import asdict
from datetime import datetime

from bson import ObjectId
from slugify import slugify

from src.domain.tools.common import clear_none, convert_obj_ids
from src.presentation.products.dto import CommentDTO, ProductDTO
from src.repositories.products.repository import CommentRepository, ProductRepository


class CommentsDomain:
    def __init__(self) -> None:
        self.repo = ProductRepository()
        self.comment = CommentRepository()

    async def add_comment(self, slug: str, user_id: str, comment: CommentDTO):
        comment = {
            **asdict(comment),
            "product": slug,
            "user_id": user_id,
            "moderate": 0,
            "created_at": datetime.now(),
        }
        result = await self.comment.create_comment(comment)
        return {"comment": result}

    async def get_comments(self, user_id):
        user_comments = await self.comment.get_user_comments(user_id)

        return {"user_comment": user_comments}

    async def get_unmoder_comments(self):
        unmoder_list = await self.comment.select_unmoder_comments()
        return convert_obj_ids(unmoder_list)

    async def moderate_comment(self, comment_id: str, result: str):
        return await self.comment.update_comment(ObjectId(comment_id), result)


class ProductDomain(CommentsDomain):

    async def add_product(self, data: ProductDTO):
        data_to_save = asdict(data)
        data_to_save["tags"].append("new")
        data_to_save.update(
            {
                "slug": slugify(data_to_save.get("title")),
                "created_at": datetime.now(),
                "available": True,
            }
        )

        new_object = await self.repo.create_product(data_to_save)

        return {"product": str(new_object.inserted_id)}

    async def retrieve_product(self, slug):
        current = await self.repo.product_by_slug(slug)

        if current is None:
            raise HTTPException(404, {"message": "product dont found"})
        comment_list = await self.repo.get_comment_by_post(slug)
        current["comments"] = comment_list
        return {"detail": current}

    async def update_product(self, slug: str, data: dict) -> dict:
        product_data = clear_none(data)

        if product_data is None:
            return {"error": "data is empty"}

        tags = product_data.pop("tags", None)
        category_titles = product_data.pop("category_titles", None)

        to_update = {"$addToSet": {}, "$set": product_data}

        if tags:
            to_update["$addToSet"].update({"tags": {"$each": tags}})

        if category_titles:
            to_update["$addToSet"].update(
                {"category_titles": {"$each": category_titles}}
            )

        document = await self.repo.update_product(slug, to_update)
        return document

    async def delete_product(self, slug):
        result = await self.repo.delete_product(slug)

        if result.deleted_count < 1:
            return {"code": 404, "message": "product not found"}

        return {"delete": result.deleted_count}

    async def get_products(self, filtering_data: dict):

        f = {}
        if filtering_data.get("tag"):
            f.update({"tags": filtering_data.get("tag")})

        if filtering_data.get("category"):
            f.update({"category_ids.title": filtering_data.get("category")})

        if filtering_data.get("price_lt"):
            f.update({"price.retail": {"$lt": filtering_data.get("price_lt")}})

        if filtering_data.get("price_gt"):
            f.update({"price.retail": {"$gt": filtering_data.get("price_gt")}})

        return await self.repo.select_product_list(f)
