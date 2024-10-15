from django.contrib import admin
from core.servers.models import Country, City, OutlineServer, OutlineServerKey


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "emoji"
    )


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_filter = ("country",)

    list_display = (
        "name",
        'country'
    )


@admin.register(OutlineServer)
class OutlineServerAdmin(admin.ModelAdmin):
    list_filter = ("city",)

    list_display = (
        "name",
        "city",
        'active',
        'created_at',
        'updated_at'

    )


@admin.register(OutlineServerKey)
class OutlineServerKeyAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "server",
    )