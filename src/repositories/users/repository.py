from bson import ObjectId
from fastapi import HTTPException
from pymongo import ReturnDocument
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
        result = await users.find_one({"_id": user_id}, {"hash_password": 0})

        result["_id"] = str(result.pop("_id"))
        return result

    async def get_user_by_email(self, email) -> dict:
        user = await users.find_one({"email": email})
        return user

    async def get_user_password(self, email) -> str:
        return await users.find_one({"email": email}, {"_id": 0, "hash_password": 1})

    async def update_user(self, email: str, data: dict, password: bool = None):

        if password:
            await users.find_one_and_update({"email": email}, data)
            return True

        update_user = await users.find_one_and_update(
            {"email": email},
            data,
            return_document=ReturnDocument.BEFORE,
            projection=self.returning_data,
        )

        return update_user

    async def update_user_privilege(
        self, email: str, role: str = None, remove: bool = None
    ):
        if remove:
            role = "default"

        update_user = await users.find_one_and_update(
            {"email": email},
            {"$set": {"role": role}},
            return_document=ReturnDocument.BEFORE,
            projection=self.returning_data,
        )

        return update_user

    @property
    def returning_data(self) -> dict:
        return {
            "_id": 0,
            "email": 1,
            "first_name": 1,
            "last_name": 1,
            "role": 1,
            "gender": 1,
            "address": 1,
        }
