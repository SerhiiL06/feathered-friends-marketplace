from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, Depends, Request

from src.domain.products.services import OrderDomain

from .dto import CreateOrderDto

order_router = APIRouter(tags=["orders"])


@order_router.post("/orders")
async def create_order(
    request: Request, data: CreateOrderDto, service: Annotated[OrderDomain, Depends()]
):
    return await service.complete_order(
        request.cookies.get("session_key"), asdict(data)
    )


@order_router.get("/orders")
async def get_order_list(service: Annotated[OrderDomain, Depends()]):
    return await service.fetch_orders()


@order_router.get("/orders/{order_id}")
async def get_order_data(order_id: str, service: Annotated[OrderDomain, Depends()]):
    return await service.fetch_one_order(order_id)
