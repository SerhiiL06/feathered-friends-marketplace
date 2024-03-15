from fastapi import APIRouter, Depends
from typing import Annotated
from src.domain.users import UserDomain
from .mapping import RegisterDTO, LoginDTO

users_router = APIRouter(prefix="/users")


@users_router.post("/register")
async def register(service: Annotated[UserDomain, Depends()], data: RegisterDTO):
    return await service.register_user(data)


@users_router.post("/login")
async def login(service: Annotated[UserDomain, Depends()], data: LoginDTO):
    return await service.login_user(data)
