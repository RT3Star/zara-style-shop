from django.db import models
from django.urls import reverse
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    """Категорія товарів"""

    name = models.CharField(max_length=100, verbose_name="Назва")
    slug = models.SlugField(unique=True, verbose_name="URL")
    description = models.TextField(blank=True, null=True, verbose_name="Опис")
    image = models.ImageField(
        upload_to="categories/", blank=True, null=True, verbose_name="Зображення"
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="children",
        verbose_name="Батьківська категорія",
    )
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Категорія"
        verbose_name_plural = "Категорії"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("shopee:category_products", args=[self.slug])


class ProductImage(models.Model):
    """Додаткові зображення товару"""

    image = models.ImageField(upload_to="products/gallery/", verbose_name="Зображення")
    alt_text = models.CharField(max_length=200, blank=True, verbose_name="Alt текст")
    is_main = models.BooleanField(default=False, verbose_name="Головне зображення")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Зображення товару"
        verbose_name_plural = "Зображення товарів"

    def __str__(self):
        return self.alt_text or f"Зображення {self.id}"


class Size(models.Model):
    """Розмір одягу"""

    name = models.CharField(max_length=10, unique=True, verbose_name="Розмір")
    sort_order = models.IntegerField(default=0, verbose_name="Порядок сортування")

    class Meta:
        verbose_name = "Розмір"
        verbose_name_plural = "Розміри"
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name


class Color(models.Model):
    """Колір одягу"""

    name = models.CharField(max_length=50, verbose_name="Назва кольору")
    code = models.CharField(
        max_length=7,
        help_text="HEX код кольору, наприклад #FF0000",
        verbose_name="HEX код",
    )

    class Meta:
        verbose_name = "Колір"
        verbose_name_plural = "Кольори"

    def __str__(self):
        return self.name


class Product(models.Model):
    """Товар (одяг)"""

    GENDER_CHOICES = [
        ("U", "Унісекс"),
        ("M", "Чоловічий"),
        ("F", "Жіночий"),
        ("K", "Дитячий"),
    ]

    # Основна інформація
    name = models.CharField(max_length=200, verbose_name="Назва")
    slug = models.SlugField(unique=True, verbose_name="URL")
    description = models.TextField(verbose_name="Опис")

    # Ціна та знижки
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ціна")
    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Ціна зі знижкою",
    )

    # Категорія та характеристики
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="Категорія",
    )
    gender = models.CharField(
        max_length=1, choices=GENDER_CHOICES, default="U", verbose_name="Стать"
    )

    # Розміри та кольори (ManyToMany)
    sizes = models.ManyToManyField(
        Size, blank=True, related_name="products", verbose_name="Доступні розміри"
    )
    colors = models.ManyToManyField(
        Color, blank=True, related_name="products", verbose_name="Доступні кольори"
    )

    # Кількість на складі
    stock = models.PositiveIntegerField(default=0, verbose_name="Кількість на складі")

    # Зображення
    image = models.ImageField(upload_to="products/", verbose_name="Головне зображення")
    images = models.ManyToManyField(
        ProductImage,
        blank=True,
        related_name="products",
        verbose_name="Додаткові зображення",
    )

    # Метрики
    views_count = models.PositiveIntegerField(
        default=0, verbose_name="Кількість переглядів"
    )

    # Статус
    is_active = models.BooleanField(default=True, verbose_name="Активний")
    is_new = models.BooleanField(default=False, verbose_name="Новинка")
    is_bestseller = models.BooleanField(default=False, verbose_name="Хіт продажів")

    # Час
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товари"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("shopee:product_detail", args=[self.slug])

    @property
    def current_price(self):
        """Повертає ціну зі знижкою або звичайну ціну"""
        return self.discount_price if self.discount_price else self.price

    @property
    def discount_percent(self):
        """Відсоток знижки"""
        if self.discount_price and self.price:
            return int((1 - self.discount_price / self.price) * 100)
        return 0

    @property
    def is_available(self):
        """Перевіряє чи є товар в наявності"""
        return self.stock > 0 and self.is_active

    @property
    def average_rating(self):
        """Середній рейтинг товару"""
        reviews = self.reviews.all()
        if reviews:
            return sum(r.rating for r in reviews) / reviews.count()
        return 0

    @property
    def reviews_count(self):
        """Кількість відгуків"""
        return self.reviews.count()


class Review(models.Model):
    """Відгуки про товар"""

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews", verbose_name="Товар"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Користувач"
    )
    rating = models.IntegerField(
        choices=[(1, "1⭐"), (2, "2⭐"), (3, "3⭐"), (4, "4⭐"), (5, "5⭐")],
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Оцінка",
    )
    comment = models.TextField(verbose_name="Коментар")

    # Для відповідей адміністратора
    is_approved = models.BooleanField(default=True, verbose_name="Схвалено")
    admin_reply = models.TextField(
        blank=True, null=True, verbose_name="Відповідь адміністратора"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Відгук"
        verbose_name_plural = "Відгуки"
        unique_together = ["product", "user"]  # Один користувач - один відгук на товар
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.product.name} - {self.rating}⭐"
