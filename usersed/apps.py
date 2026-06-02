from django.apps import AppConfig


class UsersedConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "usersed"

    def ready(self):
        import usersed.signals
