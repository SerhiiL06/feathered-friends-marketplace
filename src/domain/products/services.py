import logging
from dataclasses import asdict
from datetime import datetime

from slugify import slugify

from core.liqpay import LiqPayTools
from src.domain.tools.common import clear_none
from src.presentation.products.dto import CommentDTO, ProductDTO
from src.repositories.cart.repository import CartRepository, OrderRepository
from src.repositories.products.products import ProductRepository


class ProductDomain:
    def __init__(self) -> None:
        self.repo = ProductRepository()

    async def add_product(self, data: ProductDTO):
        data_to_save = asdict(data)
        data_to_save["tags"].append("new")
        data_to_save.update(
            {
                "slug": slugify(data_to_save.get("title")),
                "created_at": datetime.now(),
                "available": True,
            }
        )

        new_object = await self.repo.create_product(data_to_save)

        return {"product": str(new_object.inserted_id)}

    async def retrieve_product(self, slug):
        current = await self.repo.product_by_slug(slug)

        if current is None:
            return {"code": 404, "message": "product not found"}

        return {"detail": current}

    async def comment(self, slug: str, user_id: str, comment: CommentDTO):
        comment = {**asdict(comment), "user": user_id, "created_at": datetime.now()}
        result = await self.repo.add_comment(slug, comment)
        return {"update": result}

    async def update_product(self, slug: str, data: dict) -> dict:
        product_data = clear_none(data)

        if product_data is None:
            return {"error": "data is empty"}

        tags = product_data.pop("tags", None)
        category_titles = product_data.pop("category_titles", None)

        to_update = {"$addToSet": {}, "$set": product_data}

        if tags:
            to_update["$addToSet"].update({"tags": {"$each": tags}})

        if category_titles:
            to_update["$addToSet"].update(
                {"category_titles": {"$each": category_titles}}
            )

        document = await self.repo.update_product(slug, to_update)
        return document

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

            # ціна за одиницю будується в залежності від кількості замовлений одиниць
            current_price = (
                product["price"]["retail"]
                if qty < 10
                else product["price"]["wholesale"]
            )

            # вирахування ціни за певний товар
            total_price = qty * current_price

            # додавання інформації з приводу доданого продукту до корзини
            dict_data = {
                "title": product["title"],
                "slug": product["slug"],
                "price": current_price,
                "qty": qty,
                "total": total_price,
            }
            cart_data.append(dict_data)

            summary_price += total_price

        # додавання до результуючого списку корзини ціни за всі товари
        cart_data.append({"summary": summary_price})

        return cart_data


class OrderDomain(LiqPayTools):

    def __init__(self) -> None:
        self.cart = CartDomain()
        self.products = ProductDomain()
        self.repo = OrderRepository()
        super().__init__()

    async def complete_order(self, session_key, order_data: dict):
        cart_data = await self.cart.get_cart(session_key)

        # перевіряємо чи в корзині є товари
        if cart_data is None:
            return cart_data

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
        await self.repo.create_order(order)
        link_to_pay = self.generate_pay_link(order)
        return link_to_pay

    def verify_payment(self, order_id):
        r = self.check_pay_status(order_id)

        return r

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
