from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from src.domain.users.services import AuthService, UserDomain, current_user

from .dto import RegisterDTO

users_router = APIRouter(prefix="/users", tags=["auth"])


@users_router.post("/register")
async def register(service: Annotated[UserDomain, Depends()], data: RegisterDTO):
    return await service.register_user(data)


@users_router.post("/login")
async def login(
    service: Annotated[AuthService, Depends()],
    data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    return await service.get_token(data)


@users_router.get("/profile")
async def get_profile(user: current_user, service: Annotated[UserDomain, Depends()]):
    return await service.fetch_profile(user.get("user_id"))


@users_router.get("/admin/user-list")
async def get_users(user: current_user, service: Annotated[UserDomain, Depends()]):
    if user.get("role") != "admin":
        raise HTTPException(403, "you dont have permission")
    return await service.user_list()
