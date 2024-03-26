from src.repositories.products.repository import ProductRepository


class CartRepository(ProductRepository):
    async def add_to_cart(self, session_key: str, slug: str, qty: int):
        product = await self.product_by_slug(slug)
        key = f"cart:{session_key}"
        self.redis.zadd(key, mapping={str(product["_id"]): qty}, incr=True)

    async def clear_cart(self, session_key: str, specific: str = None):
        key_to_delete = f"cart:{session_key}"

        if specific:
            product_document = await self.product_by_slug(specific)
            self.redis.zrem(key_to_delete, str(product_document["_id"]))
            return {"message": "product was delete"}

        self.redis.delete(key_to_delete)
        return {"message": "cart was clear"}

    async def retrieve_cart(self, session_key: str):
        key = f"cart:{session_key}"
        cart_items = self.redis.zrange(key, 0, -1, withscores=True)

        product_dict = {}

        for item in cart_items:
            product_dict.update({item[0].decode("utf-8"): {"qty": item[1]}})

        products = await self.product_by_ids(list(product_dict.keys()))

        if not products:
            return None

        return {"products": products, "cart_data": product_dict}
