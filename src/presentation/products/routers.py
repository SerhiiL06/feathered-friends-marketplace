from typing import Annotated
from fastapi import APIRouter, Depends
from src.domain.products.products import ProductDomain
from .dto import ProductDTO

product_router = APIRouter()


@product_router.get("/products")
async def product_list(
    service: Annotated[ProductDomain, Depends()],
):
    return await service.all_products()


@product_router.post("/products")
async def create_product(
    service: Annotated[ProductDomain, Depends()], data: ProductDTO
):
    return await service.add_product(data)


@product_router.get("/products/{slug}")
async def product_detail(slug: str):
    pass


@product_router.patch("/products/{slug}")
async def product_detail(slug: str):
    pass


@product_router.delete("/products/{slug}")
async def product_detail(slug: str):
    pass
