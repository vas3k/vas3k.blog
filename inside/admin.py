from django.contrib import admin

from inside.models import Subscriber


class SubscriberAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "created_at",
        "bounces",
        "data",
        "is_confirmed",
    )
    ordering = ("-created_at",)


admin.site.register(Subscriber, SubscriberAdmin)
