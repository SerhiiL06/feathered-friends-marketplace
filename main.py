import uuid

from fastapi import FastAPI, Request

from core.config import redis_client
from src.presentation.orders.routers import order_router
from src.presentation.products.routers import product_router
from src.presentation.users.routers import users_router

app = FastAPI()


@app.middleware("http")
async def check_session(request: Request, next_call):
    response = await next_call(request)
    if not request.cookies.get("session_key"):
        response.set_cookie("session_key", uuid.uuid4(), max_age=3600)
    return response


app.include_router(users_router)
app.include_router(product_router)
app.include_router(order_router)
