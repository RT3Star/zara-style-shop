from django.db import models
from django.conf import settings
from shopee.models import Product


class Cart(models.Model):
    """Модель кошика користувача"""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="cart",
        verbose_name="Користувач",
    )
    session_key = models.CharField(
        max_length=40, null=True, blank=True, unique=True, verbose_name="Ключ сесії"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Створено")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Оновлено")

    class Meta:
        verbose_name = "Кошик"
        verbose_name_plural = "Кошики"
        ordering = ["-created_at"]

    def __str__(self):
        if self.user:
            return f"Кошик {self.user.username}"
        return f"Кошик (сесія: {self.session_key})"

    def total_price(self):
        """Загальна сума кошика"""
        return sum(item.total_price() for item in self.items.all())

    def total_items(self):
        """Загальна кількість товарів у кошику"""
        return sum(item.quantity for item in self.items.all())

    def clear(self):
        """Очистити кошик"""
        self.items.all().delete()


class CartItem(models.Model):
    """Модель товару в кошику"""

    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name="items", verbose_name="Кошик"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="cart_items",
        verbose_name="Товар",
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="Кількість")
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Ціна при додаванні"
    )

    # Опції для одягу
    size = models.CharField(max_length=10, blank=True, null=True, verbose_name="Розмір")
    color = models.CharField(max_length=50, blank=True, null=True, verbose_name="Колір")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Додано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Оновлено")

    class Meta:
        verbose_name = "Товар у кошику"
        verbose_name_plural = "Товари в кошику"
        unique_together = [
            "cart",
            "product",
            "size",
            "color",
        ]  # Унікальність з урахуванням розміру/кольору

    def __str__(self):
        return f"{self.product.name} x {self.quantity} = {self.total_price()} грн"

    def total_price(self):
        """Вартість позиції"""
        return self.price * self.quantity

    def save(self, *args, **kwargs):
        """При збереженні оновлюємо ціну товару"""
        if not self.price:
            self.price = self.product.current_price
        super().save(*args, **kwargs)
