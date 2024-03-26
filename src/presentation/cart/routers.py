from typing import Annotated

from fastapi import APIRouter, Depends, Request

from src.domain.cart.services import CartDomain

cart_router = APIRouter(prefix="/cart", tags=["cart"])


@cart_router.get("/")
async def fetch_cart_data(request: Request, service: Annotated[CartDomain, Depends()]):
    return await service.get_cart_data(request.cookies.get("session_key"))


@cart_router.post("/")
async def clear_cart(request: Request, service: Annotated[CartDomain, Depends()]):
    return service.delete_cart(request.cookies.get("session_key"))


@cart_router.post("/{product_slug}")
async def clear_specific(
    request: Request, product_slug: str, service: Annotated[CartDomain, Depends()]
):
    return await service.delete_cart(request.cookies.get("session_key"), product_slug)
