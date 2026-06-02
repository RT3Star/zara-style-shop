from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Автоматично створює профіль при реєстрації користувача"""
    if created:
        # Перевіряємо чи ще немає профілю
        if not hasattr(instance, "profile"):
            UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Автоматично зберігає профіль при збереженні користувача"""
    # Перевіряємо, чи існує профіль
    if hasattr(instance, "profile"):
        instance.profile.save()
