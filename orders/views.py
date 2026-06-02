from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.contrib.auth import login
from django_ratelimit.decorators import ratelimit

from .models import Order, OrderItem
from .forms import OrderCreateForm
from cart.models import Cart, CartItem
from .email import send_order_confirmation_email, send_order_status_update_email


@ratelimit(key="ip", rate="5/m", method="POST")
def order_create_view(request):
    """Створення замовлення (для всіх користувачів)"""

    # Перевірка на обмеження частоти
    was_limited = getattr(request, "limited", False)
    if was_limited and request.method == "POST":
        messages.error(request, "Забагато спроб. Зачекайте трохи.")
        return redirect("cart:cart_detail")

    # Отримуємо кошик
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart = Cart.objects.filter(session_key=session_key, user=None).first()

    if not cart or cart.total_items() == 0:
        messages.warning(request, "Ваш кошик порожній")
        return redirect("cart:cart_detail")

    if request.method == "POST":
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)

            if not request.user.is_authenticated:
                from usersed.models import CustomUser

                email = form.cleaned_data.get("email")
                password = form.cleaned_data.get("password")

                user = CustomUser.objects.filter(email=email).first()
                if not user:
                    username = email.split("@")[0]
                    base_username = username
                    counter = 1
                    while CustomUser.objects.filter(username=username).exists():
                        username = f"{base_username}{counter}"
                        counter += 1

                    if not password:
                        import secrets
                        import string

                        alphabet = string.ascii_letters + string.digits
                        password = "".join(secrets.choice(alphabet) for i in range(10))
                        send_password = True
                    else:
                        send_password = False

                    user = CustomUser.objects.create_user(
                        username=username, email=email, password=password
                    )
                    user.first_name = form.cleaned_data.get("first_name", "")
                    user.last_name = form.cleaned_data.get("last_name", "")
                    user.save()

                    if send_password:
                        try:
                            from django.core.mail import send_mail

                            send_mail(
                                subject="Ваш пароль для входу",
                                message=f"Вітаємо! Ваш акаунт створено.\n\nEmail: {email}\nПароль: {password}\n\nРекомендуємо змінити пароль після входу в особистий кабінет.",
                                from_email="noreply@zarastyle.com",
                                recipient_list=[email],
                                fail_silently=False,
                            )
                            messages.info(request, f"Пароль надіслано на email {email}")
                        except:
                            pass

                order.user = user
                login(request, user)
                messages.success(
                    request,
                    f"Акаунт створено! Ви можете увійти з email {email} та вашим паролем.",
                )
            else:
                order.user = request.user

            order.subtotal = cart.total_price()
            order.total_price = cart.total_price() + order.delivery_price
            order.save()

            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    product_name=cart_item.product.name,
                    product_price=cart_item.price,
                    quantity=cart_item.quantity,
                    size=cart_item.size,
                    color=cart_item.color,
                )

                product = cart_item.product
                product.stock -= cart_item.quantity
                product.save()

            cart.items.all().delete()

            try:
                send_order_confirmation_email(order)
                messages.success(
                    request,
                    f"Замовлення #{order.id} успішно створено! Підтвердження надіслано на email {order.email}",
                )
            except Exception:
                messages.success(request, f"Замовлення #{order.id} успішно створено!")

            return redirect("orders:order_detail", order_id=order.id)
    else:
        if request.user.is_authenticated:
            initial_data = {
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "email": request.user.email,
                "phone": request.user.phone if hasattr(request.user, "phone") else "",
                "address": (
                    request.user.address if hasattr(request.user, "address") else ""
                ),
                "city": request.user.city if hasattr(request.user, "city") else "",
            }
        else:
            initial_data = {}
        form = OrderCreateForm(initial=initial_data)

    context = {
        "form": form,
        "cart": cart,
        "total_items": cart.total_items(),
        "subtotal": cart.total_price(),
        "delivery_price": 50,
        "total": cart.total_price() + 50,
    }
    return render(request, "orders/order_create.html", context)


@login_required
def order_detail_view(request, order_id):
    """Деталі замовлення"""
    order = get_object_or_404(Order, id=order_id, user=request.user)

    context = {
        "order": order,
        "items": order.items.all(),
        "status_badge": order.get_status_badge(),
        "status_emoji": order.get_status_emoji(),
    }
    return render(request, "orders/order_detail.html", context)


@login_required
def order_list_view(request):
    """Список замовлень користувача"""
    orders = Order.objects.filter(user=request.user).order_by("-created_at")

    paginator = Paginator(orders, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "orders": page_obj,
    }
    return render(request, "orders/order_list.html", context)


@login_required
def order_cancel_view(request, order_id):
    """Скасування замовлення"""
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status in ["pending", "processing"]:
        old_status = order.status
        order.status = "cancelled"
        order.save()

        for item in order.items.all():
            product = item.product
            product.stock += item.quantity
            product.save()

        try:
            send_order_status_update_email(order, old_status, "cancelled")
            messages.success(request, f"Замовлення #{order.id} скасовано")
        except Exception:
            messages.success(request, f"Замовлення #{order.id} скасовано")
    else:
        messages.error(request, "Неможливо скасувати це замовлення")

    return redirect("orders:order_detail", order_id=order.id)


@login_required
def order_repeat_view(request, order_id):
    """Повторити замовлення (додати всі товари в кошик)"""
    order = get_object_or_404(Order, id=order_id, user=request.user)

    cart, created = Cart.objects.get_or_create(user=request.user)

    for item in order.items.all():
        if item.product.stock >= item.quantity and item.product.is_active:
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=item.product,
                defaults={
                    "quantity": item.quantity,
                    "price": item.product_price,
                    "size": item.size,
                    "color": item.color,
                },
            )
            if not created:
                cart_item.quantity += item.quantity
                cart_item.save()

    messages.success(request, "Товари додано до кошика")
    return redirect("cart:cart_detail")


@login_required
def order_tracking_view(request, order_id):
    """Відстеження замовлення"""
    order = get_object_or_404(Order, id=order_id, user=request.user)

    tracking_steps = [
        {
            "status": "pending",
            "title": "Замовлення створено",
            "description": "Ваше замовлення прийнято в обробку",
        },
        {
            "status": "processing",
            "title": "Обробка замовлення",
            "description": "Замовлення готується до відправки",
        },
        {
            "status": "shipped",
            "title": "Відправлено",
            "description": f'Трек-номер: {order.delivery_tracking or "очікується"}',
        },
        {
            "status": "delivered",
            "title": "Доставлено",
            "description": "Замовлення доставлено отримувачу",
        },
    ]

    current_step = 0
    for i, step in enumerate(tracking_steps):
        if step["status"] == order.status:
            current_step = i
            break

    context = {
        "order": order,
        "tracking_steps": tracking_steps,
        "current_step": current_step,
    }
    return render(request, "orders/order_tracking.html", context)
