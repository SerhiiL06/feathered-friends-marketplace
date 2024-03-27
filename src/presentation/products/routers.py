from dataclasses import asdict
from typing import Annotated, Literal

from fastapi import APIRouter, Body, Depends, Request

from src.domain.cart.services import CartDomain
from src.domain.products.bookmarks import BookmarkDomain
from src.domain.products.services import CommentDTO, ProductDomain
from src.domain.users.services import current_user

from .dto import ProductDTO

product_router = APIRouter()


@product_router.get("/products", tags=["products"])
async def fetch_product_list(
    service: Annotated[ProductDomain, Depends()],
    title: str = None,
    tag: str = None,
    category: Literal["for dogs", "for cats", "for fish"] = None,
    price_gt: int = None,
    price_lt: int = None,
):
    filtering_data = {
        "title": title,
        "tag": tag,
        "category": category,
        "price_gt": price_gt,
        "price_lt": price_lt,
    }

    return await service.get_products(filtering_data)


@product_router.post("/products", tags=["products"])
async def create_product(
    user: current_user, service: Annotated[ProductDomain, Depends()], data: ProductDTO
):

    if user.get("role") != "admin":
        return {"error": "permission danied"}
    return await service.add_product(data)


@product_router.get("/products/{slug}", tags=["products"])
async def product_detail(service: Annotated[ProductDomain, Depends()], slug: str):
    return await service.retrieve_product(slug)


@product_router.patch("/products/{slug}", tags=["products"])
async def update_product(
    user: current_user,
    service: Annotated[ProductDomain, Depends()],
    data: ProductDTO,
    slug: str,
):
    if user.get("role") != "admin":
        return {"error": "permission danied"}
    return await service.update_product(slug, asdict(data))


@product_router.delete("/products/{slug}", tags=["products"])
async def delete_product(service: Annotated[ProductDomain, Depends()], slug: str):
    return await service.delete_product(slug)


@product_router.post("/products/{slug}/comment", tags=["comments"])
async def add_comment_to_product(
    user: current_user,
    service: Annotated[ProductDomain, Depends()],
    slug: str,
    data: CommentDTO,
):
    return await service.add_comment(slug, user.get("user_id"), data)


@product_router.get("/admin/comments", tags=["comments"])
async def fetch_unmoder_comments(
    user: current_user, service: Annotated[ProductDomain, Depends()]
):

    return await service.get_unmoder_comments()


@product_router.patch("/admin/comments/{comment_id}/", tags=["comments"])
async def patch_comment(
    user: current_user,
    comment_id: str,
    service: Annotated[ProductDomain, Depends()],
    result: str = Body(pattern="approve|rejex"),
):
    if user.get("role") != "admin":
        return {"error": "permission danied"}
    return await service.moderate_comment(comment_id, result)


@product_router.post("/products/{slug}/add-to-bookmark", tags=["bookmarks"])
async def bookmark_action(
    service: Annotated[BookmarkDomain, Depends()], request: Request, slug: str
):
    return await service.update_bookmark(request.cookies.get("session_key"), slug)


@product_router.get("/bookmarks", tags=["bookmarks"])
async def bookmark_list(
    service: Annotated[BookmarkDomain, Depends()], request: Request
):
    return await service.bookmarks_list(request.cookies.get("session_key"))


@product_router.post("/products/{slug}/add-to-cart", tags=["cart"])
async def add_product_to_cart(
    service: Annotated[CartDomain, Depends()],
    request: Request,
    slug: str,
    qty: int = Body(),
):
    return await service.add_to_cart(request.cookies.get("session_key"), slug, qty)
