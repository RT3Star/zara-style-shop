from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class CustomUser(AbstractUser):
    """Розширена модель користувача для магазину одягу"""

    phone = models.CharField(
        max_length=20, blank=True, null=True, verbose_name="Телефон"
    )
    address = models.TextField(blank=True, null=True, verbose_name="Адреса")

    # Додаткові поля для магазину одягу
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Місто")
    postal_code = models.CharField(
        max_length=10, blank=True, null=True, verbose_name="Поштовий індекс"
    )

    class Meta:
        verbose_name = "Користувач"
        verbose_name_plural = "Користувачі"
        ordering = ["-date_joined"]

    def __str__(self):
        return self.username

    def get_full_name(self):
        """Повертає повне ім'я або username"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    def get_orders_count(self):
        """Кількість замовлень користувача"""
        return self.orders.filter(status="delivered").count()

    def get_total_spent(self):
        """Сума всіх замовлень користувача"""
        return (
            self.orders.filter(status="delivered").aggregate(
                total=models.Sum("total_price")
            )["total"]
            or 0
        )


class UserProfile(models.Model):
    """Профіль користувача (додаткова інформація)"""

    GENDER_CHOICES = [
        ("M", "Чоловіча"),
        ("F", "Жіноча"),
        ("O", "Інше"),
    ]

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Користувач",
    )
    bio = models.TextField(blank=True, null=True, verbose_name="Про себе")
    avatar = models.ImageField(
        upload_to="avatars/", blank=True, null=True, verbose_name="Аватар"
    )
    birth_date = models.DateField(blank=True, null=True, verbose_name="Дата народження")
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True,
        null=True,
        verbose_name="Стать",
    )

    # Налаштування сповіщень
    newsletter_subscription = models.BooleanField(
        default=False, verbose_name="Підписка на новини"
    )
    email_notifications = models.BooleanField(
        default=True, verbose_name="Email сповіщення"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Профіль"
        verbose_name_plural = "Профілі"

    def __str__(self):
        return f"Профіль {self.user.username}"

    @property
    def age(self):
        """Обчислює вік користувача"""
        if self.birth_date:
            from datetime import date

            today = date.today()
            return (
                today.year
                - self.birth_date.year
                - (
                    (today.month, today.day)
                    < (self.birth_date.month, self.birth_date.day)
                )
            )
        return None


# Сигнали для автоматичного створення профілю
@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """Автоматично створює профіль при реєстрації користувача"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    """Автоматично зберігає профіль при збереженні користувача"""
    if hasattr(instance, "profile"):
        instance.profile.save()
