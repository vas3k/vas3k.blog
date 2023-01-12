from django.contrib import admin

from users.models import User


class UsersAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "username",
        "city",
        "country",
        "created_at",
        "vas3k_club_slug",
        "patreon_id",
        "telegram_id",
        "is_banned",
    )
    ordering = ("-created_at",)


admin.site.register(User, UsersAdmin)
