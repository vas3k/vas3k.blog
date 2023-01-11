from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "notifications"

    def ready(self):
        pass
        # register signals here
        # from notifications.signals.comments import create_comment  # NOQA
