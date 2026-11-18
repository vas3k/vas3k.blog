from importlib import import_module

from django.apps import AppConfig


class TranslationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "translations"

    def ready(self):
        import_module("translations.signals")
