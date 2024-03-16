from typing import Annotated, Literal
from fastapi import APIRouter, Depends, Body, Request
from src.domain.products.services import ProductDomain
from src.domain.products.bookmarks import BookmarkDomain
from .dto import ProductDTO, CommentDTO

product_router = APIRouter()


@product_router.get("/products")
async def product_list(
    service: Annotated[ProductDomain, Depends()],
    tag: str = None,
    category: Literal["for dogs", "for cats", "for fish"] = None,
    price_gt: int = None,
    price_lt: int = None,
):
    filtering_data = {
        "tag": tag,
        "category": category,
        "price_gt": price_gt,
        "price_lt": price_lt,
    }
    return await service.all_products(filtering_data)


@product_router.post("/products")
async def create_product(
    service: Annotated[ProductDomain, Depends()], data: ProductDTO
):
    return await service.add_product(data)


@product_router.get("/products/{slug}")
async def product_detail(service: Annotated[ProductDomain, Depends()], slug: str):
    return await service.retrieve_product(slug)


@product_router.patch("/products/{slug}")
async def product_detail(slug: str):
    pass


@product_router.delete("/products/{slug}")
async def delete_product(service: Annotated[ProductDomain, Depends()], slug: str):
    return await service.delete_product(slug)


@product_router.post("/products/{slug}/comment")
async def comment_product(
    service: Annotated[ProductDomain, Depends()], slug: str, data: str = Body()
):
    return await service.comment(slug, data)


@product_router.post("/products/{slug}/add-to-bookmark")
async def bookmark_action(
    service: Annotated[BookmarkDomain, Depends()], request: Request, slug: str
):
    return await service.update_bookmark(request.cookies.get("session_key"), slug)


@product_router.get("/bookmarks")
async def bookmark_list(
    service: Annotated[BookmarkDomain, Depends()], request: Request
):
    return await service.bookmarks_list(request.cookies.get("session_key"))
