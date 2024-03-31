from datetime import datetime, timedelta
from typing import Annotated
from dataclasses import asdict
import jwt
from bson import ObjectId
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext

from core import config
from core.config import redis_client
from src.domain.tools.common import clear_none
from src.presentation.users.dto import RegisterDTO, RoleEnum
from src.repositories.users.repository import UserRepository

bcrypt = CryptContext(schemes=["bcrypt"])


bearer = OAuth2PasswordBearer(tokenUrl="users/login")


class UserDomain:

    def __init__(self) -> None:
        self.repo = UserRepository()

    async def register_user(self, data: RegisterDTO, admin=None):

        self.__check_passwords(data)

        register_data = asdict(data)
        register_data.pop("password2")
        register_data.update(
            {
                "hash_password": bcrypt.hash(register_data.pop("password1")),
                "role": RoleEnum.client.name if not admin else RoleEnum.admin.name,
                "created_at": datetime.now(),
            }
        )

        user_id = await self.repo.create_user(register_data)
        return {"user_id": str(user_id)}

    async def fetch_profile(self, user_id: str):
        result = await self.repo.get_user_by_id(ObjectId(user_id))

        return {"profile": result}

    async def update_profile(self, email: str, data: dict, password=None):
        data_to_update = {}
        data_to_update["$set"] = clear_none(data)

        if not data_to_update["$set"] is None:
            return {"error": "data is empty"}

        if data_to_update.get("address"):
            data_to_update.update(
                {"$addToSet": {"address": data_to_update.pop("address")}}
            )

        updated_profile = await self.repo.update_user(email, data_to_update, password)
        return {"update": updated_profile}

    async def set_password(self, email, data: dict):
        check_spam = self.throlling_password_changes(email)
        if check_spam:
            return {"error": f"u can try againg after {check_spam} seconds"}

        compare_result = await self.compare_password(email, data.get("old_password"))

        if compare_result is False:
            self.__update_spam_status(email)

        self.__check_passwords(data)

        to_update = {"hash_password": bcrypt.hash(data.get("password1"))}
        await self.update_profile(email, to_update, password=True)
        return {"ok": "update"}

    async def user_list(self):
        result = await self.repo.get_users()

        return {"users": result}

    async def change_user_privilege(
        self, email: str, role: RoleEnum | None, remove: bool = None
    ):
        if role is None and remove is None:
            raise HTTPException(
                400, {"error": "function without parameters is not work"}
            )

        update_user = await self.repo.update_user_privilege(email, role.name, remove)
        return {"update": update_user}

    async def compare_password(self, email, old_pw):
        user = await self.repo.get_user_password(email)

        result = bcrypt.verify(old_pw, user["hash_password"])
        return result

    @classmethod
    def __update_spam_status(cls, email: str):
        redis_client.incrby(f"spam_contlor:{email}", 1)
        redis_client.expire(f"spam_contlor:{email}", 360)

        if int(redis_client.get(f"spam_contlor:{email}")) > 3:
            redis_client.set(f"block:{email}", 1, 60)
            raise HTTPException(400, {"error": "rate limit"})

    @classmethod
    def throlling_password_changes(cls, email) -> bool:
        block_key = f"block:{email}"
        if redis_client.get(block_key):
            return redis_client.ttl(block_key)

        return False

    @classmethod
    def __check_passwords(cls, data: dict) -> dict | None:

        if data.password1 != data.password2:
            raise HTTPException(
                400, {"error": "function without parameters is not work"}
            )


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
        token = self.__generate_token(
            current_user["_id"], current_user["email"], current_user["role"]
        )
        return token

    @classmethod
    def verify_token(cls, token: str) -> dict:
        data = jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])

        if datetime.now() > datetime.fromtimestamp(data.get("exp")):
            raise HTTPException(status_code=403, detail={"error": "token exp"})

        return data

    @classmethod
    def __generate_token(cls, user_id: ObjectId, email: str, role: str) -> dict:
        exp = datetime.now() + timedelta(hours=1)
        payload = {"user_id": str(user_id), "email": email, "role": role, "exp": exp}
        token = jwt.encode(payload, config.SECRET_KEY, algorithm="HS256")
        return {"access_token": token, "token_type": "bearer"}


auth = AuthService()


def authenticated(token: Annotated[str, Depends(bearer)]):
    if token is None:
        raise jwt.PyJWTError()
    return auth.verify_token(token)


current_user = Annotated[dict, Depends(authenticated)]
