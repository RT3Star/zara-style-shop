from django.db import models
from django.conf import settings
from shopee.models import Product


class Order(models.Model):

    STATUS_CHOICES = [
        ("pending", "🟡 Очікує оплати"),
        ("processing", "🔵 В обробці"),
        ("shipped", "📦 Відправлено"),
        ("delivered", "✅ Доставлено"),
        ("cancelled", "❌ Скасовано"),
        ("refunded", "🔄 Повернуто"),
    ]

    PAYMENT_CHOICES = [
        ("cash", "Готівка при отриманні"),
        ("card", "Карткою онлайн"),
        ("bank", "Банківський переказ"),
    ]

    DELIVERY_CHOICES = [
        ("nova_poshta", "Нова Пошта"),
        ("ukrposhta", "Укрпошта"),
        ("courier", "Кур'єром по місту"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="Користувач",
    )

    first_name = models.CharField(max_length=100, verbose_name="Ім'я")
    last_name = models.CharField(max_length=100, verbose_name="Прізвище")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Телефон")

    address = models.TextField(verbose_name="Адреса")
    city = models.CharField(max_length=100, verbose_name="Місто")
    postal_code = models.CharField(
        max_length=20, blank=True, verbose_name="Поштовий індекс"
    )

    delivery_method = models.CharField(
        max_length=20,
        choices=DELIVERY_CHOICES,
        default="nova_poshta",
        verbose_name="Спосіб доставки",
    )
    delivery_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Вартість доставки"
    )
    delivery_tracking = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Трек-номер"
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_CHOICES,
        default="cash",
        verbose_name="Спосіб оплати",
    )
    is_paid = models.BooleanField(default=False, verbose_name="Оплачено")
    paid_at = models.DateTimeField(blank=True, null=True, verbose_name="Дата оплати")

    subtotal = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Сума без доставки"
    )
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Загальна сума"
    )

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending", verbose_name="Статус"
    )


    comment = models.TextField(
        blank=True, null=True, verbose_name="Коментар до замовлення"
    )
    admin_comment = models.TextField(
        blank=True, null=True, verbose_name="Коментар адміністратора"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Створено")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Оновлено")

    class Meta:
        verbose_name = "Замовлення"
        verbose_name_plural = "Замовлення"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Замовлення #{self.id} - {self.first_name} {self.last_name}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_status_badge(self):
        badges = {
            "pending": "warning",
            "processing": "info",
            "shipped": "primary",
            "delivered": "success",
            "cancelled": "danger",
            "refunded": "secondary",
        }
        return badges.get(self.status, "secondary")

    def get_status_emoji(self):
        emojis = {
            "pending": "🟡",
            "processing": "🔵",
            "shipped": "📦",
            "delivered": "✅",
            "cancelled": "❌",
            "refunded": "🔄",
        }
        return emojis.get(self.status, "⚪")


class OrderItem(models.Model):

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items", verbose_name="Замовлення"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="order_items",
        verbose_name="Товар",
    )

    product_name = models.CharField(max_length=200, verbose_name="Назва товару")
    product_price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Ціна"
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="Кількість")

    size = models.CharField(max_length=10, blank=True, null=True, verbose_name="Розмір")
    color = models.CharField(max_length=50, blank=True, null=True, verbose_name="Колір")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Товар у замовленні"
        verbose_name_plural = "Товари в замовленні"

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"

    def total_price(self):
        return self.product_price * self.quantity
