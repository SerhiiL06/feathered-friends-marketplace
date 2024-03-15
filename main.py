from fastapi import FastAPI
from src.presentation.routers import users_router
from src.presentation.products.routers import product_router

app = FastAPI()


app.include_router(users_router)
app.include_router(product_router)
