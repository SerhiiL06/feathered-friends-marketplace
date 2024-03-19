from datetime import datetime, timedelta
from typing import Annotated

import jwt
from bson import ObjectId
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext

from core import config
from src.presentation.users.dto import LoginDTO, RegisterDTO
from src.repositories.users.repository import UserRepository

bcrypt = CryptContext(schemes=["bcrypt"])


bearer = OAuth2PasswordBearer(tokenUrl="users/login")


class UserDomain:

    def __init__(self) -> None:
        self.repo = UserRepository()

    async def register_user(self, data: RegisterDTO):
        errors = self.validate_registration(data)

        if errors is not None:
            raise HTTPException(400, errors)
        hash_password = bcrypt.hash(data.password1)
        register_data = {"email": data.email, "hash_password": hash_password}
        user_id = await self.repo.create_user(register_data)
        return {"user_id": str(user_id)}

    @classmethod
    def validate_registration(cls, data: dict) -> dict | None:
        error_pack = {}
        if data.password1 != data.password2:
            error_pack.update({"password": "password must be the same"})

        if error_pack:
            errors = {"code": status.HTTP_400_BAD_REQUEST, "messages": error_pack}
            return errors
        return None


class AuthService:
    def __init__(self) -> None:
        self.repo = UserRepository()

    async def get_token(self, data: OAuth2PasswordRequestForm) -> dict:
        current_user = await self.repo.get_user_by_email(data.username)
        if current_user is None:
            return {"error": "username or password is wrong"}
        verify = bcrypt.verify(data.password, current_user["hash_password"])
        if not verify:
            return {"error": "username or password is wrong"}
        token = self.__generate_token(current_user["_id"], current_user["email"])
        return token

    @classmethod
    def verify_token(cls, token: str) -> dict:
        data = jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])

        if datetime.now() > datetime.fromtimestamp(data.get("exp")):
            raise HTTPException(status_code=403, detail={"error": "token exp"})

        return data

    @classmethod
    def __generate_token(cls, user_id: ObjectId, email: str) -> dict:
        exp = datetime.now() + timedelta(hours=1)
        payload = {"user_id": str(user_id), "email": email, "exp": exp}
        token = jwt.encode(payload, config.SECRET_KEY, algorithm="HS256")
        return {"access_token": token, "token_type": "bearer"}


auth = AuthService()


def authenticated(token: Annotated[str, Depends(bearer)]):
    if token is None:
        raise jwt.PyJWTError()
    return auth.verify_token(token)


current_user = Annotated[dict, Depends(authenticated)]
