import os

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from redis import Redis

load_dotenv()
client = AsyncIOMotorClient()
redis_client = Redis()

db = client["marketplace"]


products = db["products"]
comments = db["comments"]
orderds = db["orders"]
categories = db["categories"]
users = db["users"]


class RedisTools:

    @property
    def connect_redis(self):
        return Redis()


PUBLIC_KEY = os.getenv("PUBLIC_KEY")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
