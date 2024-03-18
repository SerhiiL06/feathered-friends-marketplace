import os
from dataclasses import asdict
from datetime import datetime

import requests
from dotenv import load_dotenv
from slugify import slugify

from core.liqpay import LiqPay
from src.presentation.products.dto import (CommentDTO, DetailProductDTO,
                                           ProductDTO)
from src.repositories.cart.repository import CartRepository, OrderRepository
from src.repositories.products.products import ProductRepository

load_dotenv()


class ProductDomain:
    def __init__(self) -> None:
        self.repo = ProductRepository()

    async def add_product(self, data: ProductDTO):

        data_to_save = asdict(data)
        data_to_save["slug"] = slugify(data_to_save.get("title"))
        new_object = await self.repo.create_product(data_to_save)

        return {"id": str(new_object.inserted_id)}

    async def retrieve_product(self, slug):
        current = await self.repo.product_by_slug(slug)

        if current is None:
            return {"code": 404, "message": "product not found"}

        result = DetailProductDTO(
            current["title"],
            current["description"],
            current["slug"],
            current["price"],
            current["category_ids"],
            current["tags"],
            comments=current["comments"] if current.get("comments") else [],
        )
        return {"detail": result}

    async def comment(self, slug: str, comment: CommentDTO):
        comment = {"text": comment, "date": datetime.now()}
        result = await self.repo.add_comment(slug, comment)

        result.pop("_id")
        return {"update": result}

    async def delete_product(self, slug):
        result = await self.repo.delete_product(slug)

        if result.deleted_count < 1:
            return {"code": 404, "message": "product not found"}

        return {"delete": result.deleted_count}

    async def all_products(self, filtering_data: dict):

        f = {}
        if filtering_data.get("tag"):
            f.update({"tags": filtering_data.get("tag")})

        if filtering_data.get("category"):
            f.update({"category_ids.title": filtering_data.get("category")})

        if filtering_data.get("price_lt"):
            f.update({"price.retail": {"$lt": filtering_data.get("price_lt")}})

        if filtering_data.get("price_gt"):
            f.update({"price.retail": {"$gt": filtering_data.get("price_gt")}})

        return await self.repo.product_list(f)


class CartDomain:
    def __init__(self) -> None:
        self.repo = CartRepository()

    async def add_to_cart(self, session_key: str, slug: str, qty: int):
        try:
            await self.repo.add_to_cart(session_key, slug, qty)
            return {"ok": "add success"}
        except:
            return {"error": "something went wrong"}

    async def delete_cart(self, session_key: str, specific: str = None):
        result = await self.repo.clear_cart(session_key, specific)
        return result

    async def get_cart(self, session_key: str) -> list:
        format_data = await self.repo.user_cart(session_key)

        if format_data is None:
            return format_data

        products, product_dict = format_data.get("products"), format_data.get(
            "product_dict"
        )

        cart_data = self.generate_cart_data(products, product_dict)

        return cart_data

    @staticmethod
    def generate_cart_data(product_list: list, product_dict: dict) -> list:
        cart_data = []
        summary_price = 0

        for product in product_list:
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


class LiqPayTools:
    PUBLIC_KEY = os.getenv("PUBLIC_KEY")
    PRIVATE_KEY = os.getenv("PRIVATE_KEY")

    def __init__(self):
        self.liqpay = LiqPay(self.PUBLIC_KEY, self.PRIVATE_KEY)

    def generate_pay_link(self, order_data):

        description = f"Order by {order_data['recipient_data']['user']['first_name']} {order_data['recipient_data']['user']['first_name']}"
        # Дані для відправки на LiqPay
        data = {
            "version": "3",
            "public_key": self.PUBLIC_KEY,
            "private_key": self.PRIVATE_KEY,
            "action": "pay",
            "amount": order_data["total_price"],
            "currency": "UAH",
            "result_url": f"http://127.0.0.1:8000/success-pay",
            "server_url": f"http://127.0.0.1:8000/verify-order/",
            "description": description,
            "order_id": "1",
        }

        data_to_sign = self.liqpay.data_to_sign(data)

        params = {"data": data_to_sign, "signature": self.liqpay.cnb_signature(data)}
        try:
            response = requests.post(
                url="https://www.liqpay.ua/api/3/checkout/", data=params
            )

            if response.status_code == 200:
                return response.url

            return response.status_code
        except:
            return 400


class OrderDomain:
    PUBLIC_KEY = os.getenv("PUBLIC_KEY")
    PRIVATE_KEY = os.getenv("PRIVATE_KEY")

    def __init__(self) -> None:
        self.cart = CartDomain()
        self.products = ProductDomain()
        self.repo = OrderRepository()
        self.lq = LiqPayTools()

    async def complete_order(self, session_key, order_data: dict):
        cart_data = await self.cart.get_cart(session_key)

        # перевіряємо чи в корзині є товари
        if cart_data is None:
            return None

        # створюємо екземпляр замовлення
        order = {}
        order["items_line"] = cart_data[:-1]
        order["status"] = "no pay"
        order["created_date"] = datetime.now()

        order.update(
            {
                "recipient_data": {
                    "user": {
                        "first_name": order_data.get("first_name"),
                        "last_name": order_data.get("last_name"),
                    },
                    "address": {
                        "city": order_data.get("city"),
                        "zip_code": order_data.get("zip_code"),
                    },
                }
            }
        )

        order["total_price"] = cart_data[-1].get("summary")

        # очищаємо корзину після створення екземпляру замовлення
        await self.cart.delete_cart(session_key)

        # зберігаємо замовлення
        new_order = await self.repo.create_order(order)
        link_to_pay = self.lq.generate_pay_link(order)
        return link_to_pay

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
