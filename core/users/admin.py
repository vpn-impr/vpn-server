from typing import Any

from django.contrib import admin

from core.users.models import User, TelegramUser


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    filter_horizontal = ("groups", "user_permissions")

    list_display = (
        "username",
        "is_active",
        "is_staff",
        "is_superuser",
    )


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "username",
        "first_name",
        "last_name"
    )