# def user_cart(request):
#     key = request.session.session_key
#     cart_items = redis_client.zrange("cart:" + key, 0, -1, withscores=True)
#     ids = []

#     for el in cart_items:
#         ids.append(int(el[0]))

#     products = Product.objects.filter(id__in=ids)

#     cart_data = []

#     for product in products:
#             dict_data = {
#                 "product": product,
#                 "price": Decimal(cart_items[ids.index(product.id)][1]) * product.price,
#                 "qty": int(cart_items[ids.index(product.id)][1]),
#             }
#             cart_data.append(dict_data)

#     total = redis_client.get("total:" + key)

#         context = {"products": cart_data}
#         if total:
#             context["total_price"] = float(total)


# def update_cart(request):
#     key = request.session.session_key
#     product = request.POST["product_id"]
#     qty = int(request.POST["quantity"])

#     last_product_count = redis_client.zscore("cart:" + key, product)
#     redis_client.zadd("cart:" + key, mapping={product: qty})

#     old_price = last_product_count * float(request.POST["price"])
#     new_price = qty * float(request.POST["price"])

#     redis_client.incrbyfloat("total:" + key, new_price - old_price)
