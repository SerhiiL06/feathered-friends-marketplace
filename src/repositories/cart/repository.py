from bson import ObjectId

from core.config import RedisTools, orderds
from src.repositories.products.products import ProductRepository


class CartRepository:
    def __init__(self) -> None:
        client = RedisTools()

        self.__redis = client.connect_redis
        self.repo = ProductRepository()

    async def add_to_cart(self, session_key: str, slug: str, qty: int):
        product = await self.repo.product_by_slug(slug)
        key = f"cart:{session_key}"
        self.__redis.zadd(key, mapping={str(product["_id"]): qty}, incr=True)

    async def clear_cart(self, session_key: str, specific: str = None):
        key_to_delete = f"cart:{session_key}"

        if specific:
            product_document = await self.repo.product_by_slug(specific)
            self.__redis.zrem(key_to_delete, str(product_document["_id"]))
            return {"message": "product was delete"}

        self.__redis.delete(key_to_delete)
        return {"message": "cart was clear"}

    async def user_cart(self, session_key: str):
        key = f"cart:{session_key}"
        cart_items = self.__redis.zrange(key, 0, -1, withscores=True)

        product_dict = {}

        for item in cart_items:
            product_dict.update({item[0].decode("utf-8"): {"qty": item[1]}})

        products = await self.repo.product_by_ids(list(product_dict.keys()))

        if not products:
            return None

        result = {"products": products, "product_dict": product_dict}

        return result


class OrderRepository:
    def __init__(self) -> None:
        client = RedisTools()

        self.__redis = client.connect_redis

    async def create_order(self, data: dict) -> str:

        result = await orderds.insert_one(data)

        return result

    async def retrieve_all_orders(self):
        return await orderds.find({}).sort({"created_date": -1}).to_list(None)

    async def retrieve_order(self, order_id) -> dict:
        return await orderds.find_one({"_id": ObjectId(order_id)})
