from django.apps import AppConfig


class UseraccountConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'useraccount'
    verbose_name = "Пользователи"
    verbose_name_plural = "Пользователи"

    def ready(self):
        import useraccount.signals