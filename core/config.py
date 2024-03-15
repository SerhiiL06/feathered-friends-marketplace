from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient()


db = client["marketplace"]


products = db["products"]
categories = db["categories"]
users = db["users"]
