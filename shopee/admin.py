from django.contrib import admin
from django.utils.safestring import mark_safe
from django.db.models import Count
from .models import Category, Product, ProductImage, Review, Size, Color


class ProductImageInline(admin.TabularInline):

    model = Product.images.through
    extra = 3
    verbose_name = "Зображення"
    verbose_name_plural = "Зображення"


class ReviewInline(admin.TabularInline):

    model = Review
    extra = 0
    readonly_fields = ("user", "rating", "comment", "created_at")
    can_delete = False
    verbose_name = "Відгук"
    verbose_name_plural = "Відгуки"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "slug",
        "get_image_preview",
        "product_count",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("is_active",)
    readonly_fields = ("get_image_preview", "created_at", "updated_at")

    fieldsets = (
        (
            "Основна інформація",
            {"fields": ("name", "slug", "description", "image", "get_image_preview")},
        ),
        ("Відносини", {"fields": ("parent",)}),
        ("Статус", {"fields": ("is_active",)}),
        ("Дати", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def get_image_preview(self, obj):
        if obj.image:
            return mark_safe(
                f'<img src="{obj.image.url}" width="50" height="50" style="object-fit: cover;" />'
            )
        return "Немає фото"

    get_image_preview.short_description = "Прев'ю"

    def product_count(self, obj):
        return obj.products.filter(is_active=True).count()

    product_count.short_description = "Товарів"


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):

    list_display = ("name", "sort_order", "products_count")
    list_editable = ("sort_order",)
    search_fields = ("name",)
    ordering = ("sort_order", "name")

    def products_count(self, obj):
        return obj.products.count()

    products_count.short_description = "Товарів"


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):

    list_display = ("name", "code", "color_preview", "products_count")
    search_fields = ("name",)

    def color_preview(self, obj):
        return mark_safe(
            f'<div style="width: 30px; height: 30px; background-color: {obj.code}; border: 1px solid #ccc;"></div>'
        )

    color_preview.short_description = "Колір"

    def products_count(self, obj):
        return obj.products.count()

    products_count.short_description = "Товарів"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "get_image_preview",
        "price",
        "current_price",
        "stock",
        "category",
        "is_active",
        "is_bestseller",
        "views_count",
    )
    list_filter = (
        "category",
        "is_active",
        "is_new",
        "is_bestseller",
        "gender",
        "created_at",
    )
    search_fields = ("name", "description", "slug")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("price", "stock", "is_active", "is_bestseller")
    readonly_fields = (
        "get_image_preview",
        "views_count",
        "average_rating_display",
        "created_at",
        "updated_at",
    )

    filter_horizontal = ("sizes", "colors", "images")

    fieldsets = (
        (
            "Основна інформація",
            {"fields": ("name", "slug", "description", "category", "gender")},
        ),
        (
            "Ціна та знижки",
            {
                "fields": (
                    "price",
                    "discount_price",
                    "current_price_display",
                    "discount_percent_display",
                )
            },
        ),
        ("Характеристики", {"fields": ("sizes", "colors")}),
        ("Зображення", {"fields": ("image", "get_image_preview", "images")}),
        (
            "Наявність та статус",
            {"fields": ("stock", "is_active", "is_new", "is_bestseller")},
        ),
        ("Метрики", {"fields": ("views_count", "average_rating_display")}),
        ("Дати", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    inlines = [ReviewInline]

    def get_image_preview(self, obj):
        if obj.image:
            return mark_safe(
                f'<img src="{obj.image.url}" width="50" height="50" style="object-fit: cover;" />'
            )
        return "Немає фото"

    get_image_preview.short_description = "Прев'ю"

    def current_price_display(self, obj):
        from django.utils.html import format_html

        if obj.discount_price:
            return format_html(
                '<span style="color: red;">{} грн</span> <del style="color: gray;">{} грн</del>',
                obj.discount_price,
                obj.price,
            )
        return f"{obj.price} грн"

    current_price_display.short_description = "Поточна ціна"

    def discount_percent_display(self, obj):
        if obj.discount_price:
            percent = int((1 - obj.discount_price / obj.price) * 100)
            return f"-{percent}%"
        return "-"

    discount_percent_display.short_description = "Знижка"

    def average_rating_display(self, obj):
        rating = obj.average_rating
        if rating:
            return f"⭐ {rating:.1f} / 5 ({obj.reviews_count} відгуків)"
        return "Немає відгуків"

    average_rating_display.short_description = "Рейтинг"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        from django.utils import timezone
        from datetime import timedelta

        if obj.created_at > timezone.now() - timedelta(days=30):
            obj.is_new = True
            obj.save()


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):

    list_display = (
        "product",
        "user",
        "rating",
        "comment_preview",
        "is_approved",
        "created_at",
    )
    list_filter = ("rating", "is_approved", "created_at")
    search_fields = ("product__name", "user__username", "comment")
    list_editable = ("is_approved",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Інформація", {"fields": ("product", "user", "rating", "comment")}),
        ("Модерація", {"fields": ("is_approved", "admin_reply")}),
        ("Дати", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def comment_preview(self, obj):
        return obj.comment[:50] + "..." if len(obj.comment) > 50 else obj.comment

    comment_preview.short_description = "Коментар"


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):

    list_display = ("id", "get_image_preview", "alt_text", "created_at")
    list_filter = ("created_at",)
    search_fields = ("alt_text",)
    readonly_fields = ("get_image_preview",)

    def get_image_preview(self, obj):
        if obj.image:
            return mark_safe(
                f'<img src="{obj.image.url}" width="100" height="100" style="object-fit: cover;" />'
            )
        return "Немає фото"

    get_image_preview.short_description = "Прев'ю"
