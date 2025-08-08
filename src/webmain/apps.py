from django.apps import AppConfig


class WebmainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'webmain'
    verbose_name = "Сайт"
    verbose_name_plural = "Сайт"

    def ready(self):
        import webmain.signals
