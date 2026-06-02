# shopee/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Product, Category


@receiver([post_save, post_delete], sender=Product)
@receiver([post_save, post_delete], sender=Category)
def clear_product_cache(sender, instance, **kwargs):

    cache.clear()


    print(f"[CACHE] Очищено кеш через зміну: {sender.__name__} - {instance}")
