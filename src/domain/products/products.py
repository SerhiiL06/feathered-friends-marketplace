from src.presentation.products.dto import ProductDTO, DetailProductDTO, CommentDTO
from src.repositories.products.products import ProductRepository
from dataclasses import asdict
from slugify import slugify
from datetime import datetime


class ProductDomain:
    def __init__(self) -> None:
        self.repo = ProductRepository()

    async def add_product(self, data: ProductDTO):

        data_to_save = asdict(data)
        data_to_save["slug"] = slugify(data_to_save.get("title"))
        new_object = await self.repo.create_product(data_to_save)

        return {"id": str(new_object.inserted_id)}

    async def retrieve_product(self, slug):
        current = await self.repo.product_by_slug(slug)

        if current is None:
            return {"code": 404, "message": "product not found"}

        result = DetailProductDTO(
            current["title"],
            current["description"],
            current["slug"],
            current["price"],
            current["category_ids"],
            current["tags"],
            comments=current["comments"] if current.get("comments") else [],
        )
        return {"detail": result}

    async def comment(self, slug: str, comment: CommentDTO):
        comment = {"text": comment, "date": datetime.now()}
        result = await self.repo.add_comment(slug, comment)

        result.pop("_id")
        return {"update": result}

    async def delete_product(self, slug):
        result = await self.repo.delete_product(slug)

        if result.deleted_count < 1:
            return {"code": 404, "message": "product not found"}

        return {"delete": result.deleted_count}

    async def all_products(self, filtering_data: dict):

        f = {}
        if filtering_data.get("tag"):
            f.update({"tags": filtering_data.get("tag")})

        if filtering_data.get("category"):
            f.update({"category_ids.title": filtering_data.get("category")})

        if filtering_data.get("price_lt"):
            f.update({"price.retail": {"$lt": filtering_data.get("price_lt")}})

        if filtering_data.get("price_gt"):
            f.update({"price.retail": {"$gt": filtering_data.get("price_gt")}})

        return await self.repo.product_list(f)
