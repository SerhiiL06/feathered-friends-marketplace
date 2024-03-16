from motor.motor_asyncio import AsyncIOMotorClient
from redis import Redis

client = AsyncIOMotorClient()
redis_client = Redis()

db = client["marketplace"]


products = db["products"]
categories = db["categories"]
users = db["users"]
