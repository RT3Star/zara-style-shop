from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django_ratelimit.decorators import ratelimit

from .models import Cart, CartItem
from shopee.models import Product


def get_or_create_cart(request):
    """Отримує або створює кошик для поточного користувача"""

    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)

        if request.session.session_key:
            Cart.objects.filter(session_key=request.session.session_key).exclude(
                user=request.user
            ).delete()

            try:
                session_cart = Cart.objects.get(
                    session_key=request.session.session_key, user=None
                )
                if session_cart and session_cart.items.exists():
                    for item in session_cart.items.all():
                        cart_item, created = CartItem.objects.get_or_create(
                            cart=cart,
                            product=item.product,
                            size=item.size,
                            color=item.color,
                            defaults={"quantity": item.quantity, "price": item.price},
                        )
                        if not created:
                            cart_item.quantity += item.quantity
                            cart_item.save()
                    session_cart.delete()
            except Cart.DoesNotExist:
                pass
            except Cart.MultipleObjectsReturned:
                duplicate_carts = Cart.objects.filter(
                    session_key=request.session.session_key, user=None
                )
                if duplicate_carts.count() > 1:
                    keep_cart = duplicate_carts.first()
                    for dup_cart in duplicate_carts[1:]:
                        for item in dup_cart.items.all():
                            cart_item, created = CartItem.objects.get_or_create(
                                cart=keep_cart,
                                product=item.product,
                                size=item.size,
                                color=item.color,
                                defaults={
                                    "quantity": item.quantity,
                                    "price": item.price,
                                },
                            )
                            if not created:
                                cart_item.quantity += item.quantity
                                cart_item.save()
                        dup_cart.delete()
        return cart

    else:
        if not request.session.session_key:
            request.session.create()

        session_key = request.session.session_key

        carts = Cart.objects.filter(session_key=session_key, user=None)
        if carts.count() > 1:
            keep_cart = carts.first()
            for dup_cart in carts[1:]:
                for item in dup_cart.items.all():
                    cart_item, created = CartItem.objects.get_or_create(
                        cart=keep_cart,
                        product=item.product,
                        size=item.size,
                        color=item.color,
                        defaults={"quantity": item.quantity, "price": item.price},
                    )
                    if not created:
                        cart_item.quantity += item.quantity
                        cart_item.save()
                dup_cart.delete()
            return keep_cart

        cart, created = Cart.objects.get_or_create(
            session_key=session_key, defaults={"user": None}
        )
        return cart


def cart_detail(request):
    """Відображення кошика"""
    cart = get_or_create_cart(request)

    context = {
        "cart": cart,
        "cart_items": cart.items.all().select_related("product"),
        "total_price": cart.total_price(),
        "total_items": cart.total_items(),
    }
    return render(request, "cart/cart_detail.html", context)


@require_POST
@ratelimit(key="ip", rate="30/m", method="POST")
def add_to_cart(request, product_id):
    """Додавання товару до кошика (синхронне)"""

    # Перевірка на обмеження частоти
    was_limited = getattr(request, "limited", False)
    if was_limited:
        messages.error(request, "Забагато запитів. Зачекайте трохи.")
        return redirect(request.META.get("HTTP_REFERER", "shopee:product_list"))

    product = get_object_or_404(Product, id=product_id, is_active=True)
    quantity = int(request.POST.get("quantity", 1))
    size = request.POST.get("size", "")
    color = request.POST.get("color", "")

    if quantity > product.stock:
        messages.error(
            request, f'На складі тільки {product.stock} шт. "{product.name}"'
        )
        return redirect(request.META.get("HTTP_REFERER", "shopee:product_list"))

    cart = get_or_create_cart(request)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        size=size,
        color=color,
        defaults={"quantity": quantity, "price": product.current_price},
    )

    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    messages.success(request, f'Товар "{product.name}" додано до кошика!')

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse(
            {
                "success": True,
                "message": f'Товар "{product.name}" додано до кошика',
                "cart_count": cart.total_items(),
                "cart_total": str(cart.total_price()),
            }
        )

    return redirect("cart:cart_detail")


@require_POST
def update_cart_item(request, item_id):
    """Оновлення кількості товару в кошику"""
    cart_item = get_object_or_404(CartItem, id=item_id)
    quantity = int(request.POST.get("quantity", 0))

    if quantity <= 0:
        cart_item.delete()
        messages.success(request, "Товар видалено з кошика")
    else:
        if quantity > cart_item.product.stock:
            messages.warning(request, f"На складі тільки {cart_item.product.stock} шт.")
            quantity = cart_item.product.stock
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, "Кількість оновлено")

    return redirect("cart:cart_detail")


@require_POST
def remove_from_cart(request, item_id):
    """Видалення товару з кошика"""
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    messages.success(request, "Товар видалено з кошика")
    return redirect("cart:cart_detail")


def cart_count(request):
    """Повертає кількість товарів у кошику (для AJAX)"""
    cart = get_or_create_cart(request)
    return JsonResponse({"count": cart.total_items()})


@require_POST
@ratelimit(key="ip", rate="30/m", method="POST")
def add_to_cart_ajax(request):
    """Додавання товару до кошика через AJAX"""

    # Перевірка на обмеження частоти
    was_limited = getattr(request, "limited", False)
    if was_limited:
        return JsonResponse(
            {"success": False, "message": "Забагато запитів. Зачекайте трохи."}
        )

    try:
        product_id = request.POST.get("product_id")
        quantity = int(request.POST.get("quantity", 1))

        product = get_object_or_404(Product, id=product_id, is_active=True)

        if not product.is_available:
            return JsonResponse(
                {
                    "success": False,
                    "message": f'Товар "{product.name}" відсутній в наявності!',
                }
            )

        cart = get_or_create_cart(request)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={"quantity": quantity, "price": product.current_price},
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return JsonResponse(
            {
                "success": True,
                "message": f'Товар "{product.name}" додано до кошика',
                "cart_count": cart.total_items(),
                "cart_total": str(cart.total_price()),
            }
        )

    except Product.DoesNotExist:
        return JsonResponse({"success": False, "message": "Товар не знайдено"})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})
