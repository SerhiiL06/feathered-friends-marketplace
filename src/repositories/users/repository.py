from bson import ObjectId
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

    async def get_users(self):
        result = await users.find({}).to_list(20)

        res = []

        for k, v in result.items():
            if k == "_id":
                res.append({k: (str(v))})
            else:
                res.append({k: v})
        return res

    async def get_user_by_id(self, user_id: ObjectId):
        result = await users.find_one({"_id": user_id})

        result["_id"] = str(result.pop("_id"))
        return result

    async def get_user_by_email(self, email) -> dict:
        user = await users.find_one({"email": email})
        return user
