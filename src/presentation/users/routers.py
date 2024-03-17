from typing import Annotated

from fastapi import APIRouter, Depends

from src.domain.users import UserDomain

from .dto import LoginDTO, RegisterDTO

users_router = APIRouter(prefix="/users", tags=["auth"])


@users_router.post("/register")
async def register(service: Annotated[UserDomain, Depends()], data: RegisterDTO):
    return await service.register_user(data)


@users_router.post("/login")
async def login(service: Annotated[UserDomain, Depends()], data: LoginDTO):
    return await service.login_user(data)
