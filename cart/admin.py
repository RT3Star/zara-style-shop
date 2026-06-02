from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ("product", "quantity", "price", "size", "color", "total_price")
    can_delete = False

    def total_price(self, obj):
        return obj.total_price()

    total_price.short_description = "Сума"


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "session_key",
        "total_items",
        "total_price",
        "created_at",
    )
    list_filter = ("created_at", "updated_at")
    search_fields = ("user__username", "user__email", "session_key")
    readonly_fields = ("created_at", "updated_at", "total_items", "total_price")
    inlines = [CartItemInline]

    def total_items(self, obj):
        return obj.total_items()

    total_items.short_description = "Товарів"

    def total_price(self, obj):
        return f"{obj.total_price()} грн"

    total_price.short_description = "Сума"


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = (
        "cart",
        "product",
        "quantity",
        "price",
        "size",
        "color",
        "total_price",
    )
    list_filter = ("created_at",)
    search_fields = ("cart__user__username", "product__name")
    readonly_fields = ("total_price",)

    def total_price(self, obj):
        return obj.total_price()

    total_price.short_description = "Сума"
