from dataclasses import asdict
from typing import Annotated, Literal

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from src.domain.products.services import ProductDomain
from src.domain.users.services import AuthService, UserDomain, current_user

from .dto import ChangePasswordDTO, RegisterDTO, RoleEnum, UpdateUserDTO

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


@users_router.get("/profile/comments")
async def fetch_user_comments(
    user: current_user, service: Annotated[ProductDomain, Depends()]
):
    return await service.get_comments(user.get("user_id"))


@users_router.patch("/profile")
async def update_profile_info(
    user: current_user, data: UpdateUserDTO, service: Annotated[UserDomain, Depends()]
):
    return await service.update_profile(user.get("email"), asdict(data))


@users_router.patch("/profile/set-password")
async def set_password(
    user: current_user,
    data: ChangePasswordDTO,
    service: Annotated[UserDomain, Depends()],
):
    return await service.set_password(user.get("email"), asdict(data))


@users_router.get("/admin/user-list")
async def get_users(user: current_user, service: Annotated[UserDomain, Depends()]):
    if user.get("role") != "admin":
        raise HTTPException(403, "you dont have permission")
    return await service.user_list()


@users_router.post("/admin/privilege-user")
async def get_users(
    service: Annotated[UserDomain, Depends()],
    user: current_user,
    email: str = Body(),
    remove: bool = Body(None),
    role: Literal[RoleEnum.admin, RoleEnum.manager] = Body(None),
):
    if user.get("role") != RoleEnum.admin.value:
        raise HTTPException(403, "you dont have permission")
    return await service.change_user_privilege(email, role, remove)
