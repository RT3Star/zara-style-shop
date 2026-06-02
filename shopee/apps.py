from django.apps import AppConfig


class ShopeeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "shopee"
    verbose_name = "Магазин одягу"

    def ready(self):
        """Імпортуємо сигнали при запуску додатку"""
        import shopee.signals
