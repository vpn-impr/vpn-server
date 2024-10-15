from email.policy import default

from django.db import models

from core.utils.nanoid import generate_nanoid_32


class Country(models.Model):
    id = models.CharField(
        max_length=32,
        primary_key=True,
        default=generate_nanoid_32,
        editable=False,
        unique=True
    )
    name = models.CharField(max_length=255)
    emoji = models.CharField(max_length=255, default='🏳')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'countries'

class City(models.Model):
    id = models.CharField(
        max_length=32,
        primary_key=True,
        default=generate_nanoid_32,
        editable=False,
        unique=True
    )
    name = models.CharField(max_length=255)
    country = models.ForeignKey(Country, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name}, {self.country.name} {self.country.emoji}'

    class Meta:
        db_table = 'cities'

class OutlineServer(models.Model):
    id = models.CharField(
        max_length=32,
        primary_key=True,
        default=generate_nanoid_32,
        editable=False,
        unique=True
    )
    name = models.CharField(max_length=255)
    api_url = models.CharField(max_length=10000)
    cert_sha_256 = models.CharField(max_length=10000)
    host = models.CharField(max_length=10000, default='None')
    port = models.CharField(max_length=10000, default='None')
    city = models.ForeignKey(
        City, on_delete=models.PROTECT,
        related_name='city_outline_servers',  related_query_name='city_outline_servers'
    )
    active = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    system_description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'outline_servers'

class OutlineServerKey(models.Model):
    id = models.CharField(
        max_length=32,
        primary_key=True,
        default=generate_nanoid_32,
        editable=False,
        unique=True
    )
    external_id = models.CharField(max_length=10000)
    access_key = models.CharField(max_length=10000)
    password = models.CharField(max_length=10000, default='None')
    method = models.CharField(max_length=10000, default='None')
    server = models.ForeignKey(OutlineServer, on_delete=models.PROTECT)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.external_id

    class Meta:
        db_table = 'outline_server_keys'