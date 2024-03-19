from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.domain.users.services import AuthService, UserDomain, current_user

from .dto import LoginDTO, RegisterDTO

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


@users_router.get("/test")
async def login(user: current_user):
    return {"user": user}
