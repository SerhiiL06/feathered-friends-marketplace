from src.repositories.cart.repository import CartRepository


class CartDomain:
    def __init__(self) -> None:
        self.repo = CartRepository()

    async def add_to_cart(self, session_key: str, slug: str, qty: int) -> dict:
        try:
            await self.repo.add_to_cart(session_key, slug, qty)
            return {"ok": "add success"}
        except:

            return {"error": "something went wrong"}

    async def delete_cart(self, session_key: str, specific: str = None):
        result = await self.repo.clear_cart(session_key, specific)
        return result

    async def get_cart_data(self, session_key: str) -> list:
        cart_data = await self.repo.retrieve_cart(session_key)

        if cart_data is None:
            return {"message": "cart is empty"}

        products, cart_data = (cart_data.get("products"),)
        cart_data = cart_data.get("cart_data")

        cart_data = self.generate_cart_data(products, cart_data)

        return cart_data

    @staticmethod
    def generate_cart_data(product_list: list, cart_data: dict) -> list:
        cart_data = []
        summary_price = 0

        for product in product_list:
            qty = cart_data.get(str(product["_id"]))["qty"]

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
