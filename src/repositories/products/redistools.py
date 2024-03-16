from redis import Redis
from src.repositories.products.products import ProductRepository


class RedisRepository:
    def __init__(self) -> None:
        self.redis = Redis()
        self.repo = ProductRepository()

    async def update_bookmark(self, session_key: str, product_slug):
        set_key = f"bookmark:{session_key}"

        product_exists = await self.repo.product_by_slug(product_slug)
        if product_exists is None:
            return {"code": "404", "error": "product doesnt exists"}

        if self.redis.sismember(set_key, product_slug) == 1:

            self.redis.srem(set_key, product_slug)
            return {"code": 200, "message": "delete from bookmark"}

        else:
            self.redis.sadd(set_key, product_slug)
            return {"code": 204, "message": "add complete"}

    async def get_bookmarks(self, session_key):
        set_key = f"bookmark:{session_key}"
        members = self.redis.smembers(set_key)

        return await self.repo.product_by_slug(members)
