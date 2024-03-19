from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError

from core.config import users


class UserRepository:
    async def create_user(self, data: dict) -> int:
        try:
            res = await users.insert_one(data)
            return res.inserted_id
        except DuplicateKeyError:
            raise HTTPException(
                400, {"error": "user with this email already is exists"}
            )

    async def get_user_by_email(self, email) -> dict:
        user = await users.find_one({"email": email})
        return user
