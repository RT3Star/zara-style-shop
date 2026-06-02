from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe
from .models import CustomUser, UserProfile


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "phone",
        "city",
        "is_staff",
        "date_joined",
    )
    list_filter = ("is_staff", "is_active", "date_joined")
    search_fields = ("username", "email", "first_name", "last_name", "phone", "city")
    readonly_fields = ("date_joined", "last_login")

    fieldsets = UserAdmin.fieldsets + (
        (
            "Додаткова інформація",
            {
                "fields": ("phone", "address", "city", "postal_code"),
            },
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("profile")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "get_avatar",
        "gender",
        "birth_date",
        "newsletter_subscription",
    )  # city прибрано
    list_filter = ("gender", "newsletter_subscription", "created_at")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("created_at", "updated_at", "display_avatar")

    fieldsets = (
        ("Основна інформація", {"fields": ("user", "avatar", "display_avatar", "bio")}),
        ("Особисті дані", {"fields": ("gender", "birth_date")}),
        (
            "Налаштування",
            {"fields": ("newsletter_subscription", "email_notifications")},
        ),
        ("Дати", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def get_avatar(self, obj):
        """Відображає мініатюру аватарки в списку"""
        if obj.avatar:
            return mark_safe(
                f'<img src="{obj.avatar.url}" width="50" height="50" style="border-radius: 50%;" />'
            )
        return "Немає фото"

    get_avatar.short_description = "Аватар"

    def display_avatar(self, obj):
        """Відображає велику аватарку в деталях"""
        if obj.avatar:
            return mark_safe(
                f'<img src="{obj.avatar.url}" width="150" height="150" style="border-radius: 50%;" />'
            )
        return "Немає фото"

    display_avatar.short_description = "Поточний аватар"
