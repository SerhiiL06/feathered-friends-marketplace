from datetime import datetime

from core.liqpay import LiqPayTools
from src.domain.cart.services import CartDomain
from src.repositories.orders.repository import OrderRepository


class OrderDomain(LiqPayTools):

    def __init__(self) -> None:
        self.repo = OrderRepository()
        super().__init__()

    async def complete_order(
        self, session_key, order_data: dict, cart: CartDomain = CartDomain()
    ):
        cart_data = await cart.get_cart(session_key)

        # перевіряємо чи в корзині є товари
        if cart_data is None:
            return cart_data

        # створюємо екземпляр замовлення
        order = {}
        order["items_line"] = cart_data[:-1]
        order["status"] = "no pay"
        order["created_date"] = datetime.now()
        order["recipient_data"] = {
            "user": {
                "first_name": order_data.get("first_name"),
                "last_name": order_data.get("last_name"),
            },
            "address": {
                "city": order_data.get("city"),
                "zip_code": order_data.get("zip_code"),
            },
        }
        order["total_price"] = cart_data[-1].get("summary")

        # очищаємо корзину після створення екземпляру замовлення
        await cart.delete_cart(session_key)

        # зберігаємо замовлення
        await self.repo.create_order(order)
        link_to_pay = self.generate_pay_link(order)
        return link_to_pay

    def verify_payment(self, order_id):
        status = self.check_pay_status(order_id)

        return status

    async def fetch_orders(self):
        list_of_orders = await self.repo.retrieve_all_orders()

        # Отримати рядкове представлення ObjectId для кожного документа
        list_of_orders_with_string_ids = [
            {**order, "_id": str(order["_id"])} for order in list_of_orders
        ]

        return list_of_orders_with_string_ids

    async def fetch_one_order(self, order_id):
        order = await self.repo.retrieve_order(order_id)

        order["_id"] = str(order.pop("_id"))

        return order
