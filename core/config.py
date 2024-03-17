from motor.motor_asyncio import AsyncIOMotorClient
from redis import Redis

client = AsyncIOMotorClient()
redis_client = Redis()

db = client["marketplace"]


products = db["products"]
orderds = db["orders"]
categories = db["categories"]
users = db["users"]


class RedisTools:

    @property
    def connect_redis(self):
        return Redis()
