from bson import ObjectId

from core.config import orderds
from src.repositories.cart.repository import CartRepository


class OrderRepository(CartRepository):
    async def create_order(self, data: dict) -> str:

        result = await orderds.insert_one(data)

        return result

    async def retrieve_all_orders(self, user_id: str = None):
        if user_id:
            return await orderds.find({}).sort({"created_date": -1}).to_list(None)
        return await orderds.find({}).sort({"created_date": -1}).to_list(None)

    async def retrieve_order(self, order_id: str) -> dict:
        return await orderds.find_one({"_id": ObjectId(order_id)})
