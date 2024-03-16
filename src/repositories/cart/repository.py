from core.config import RedisTools
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

    async def user_cart(self, session_key: str):
        key = f"cart:{session_key}"
        cart_items = self.__redis.zrange(key, 0, -1, withscores=True)

        ids = []
        product_dict = {}

        for el in cart_items:
            ids.append(el[0])
            product_dict.update({el[0].decode("utf-8"): {"qty": el[1]}})

        products = await self.repo.product_by_ids(ids)

        cart_data = []
        summary_price = 0

        for product in products:
            qty = product_dict.get(str(product["_id"]))["qty"]
            current_price = (
                product["price"]["retail"]
                if qty < 10
                else product["price"]["wholesale"]
            )
            total_price = qty * current_price
            dict_data = {
                "title": product["title"],
                "slug": product["slug"],
                "price": current_price,
                "qty": qty,
                "total": total_price,
            }
            cart_data.append(dict_data)
            summary_price += total_price

        cart_data.append({"summary": summary_price})

        return cart_data
