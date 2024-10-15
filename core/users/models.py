from datetime import timedelta

from attr import attributes
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.servers.models import OutlineServerKey
from core.utils.datetimes import get_now

def get_subscription_trial_date():
    return get_now() + timedelta(days=1)

class User(AbstractUser):
    pass

class TelegramUser(models.Model):
    id = models.CharField(
        max_length=32,
        primary_key=True,
        editable=False,
        unique=True
    )
    username = models.CharField(
        _("username"),
        max_length=10000,
        null=True
    )
    first_name = models.CharField(_("first name"), max_length=1500,
        null=True, blank=True)
    last_name = models.CharField(_("last name"), max_length=1500,
        null=True, blank=True)

    subscription_expire_datetime = models.DateTimeField(blank=True, null=True)
    subscription_price = models.DecimalField(max_digits=10, decimal_places=2, default=1000)

    outline_server_key = models.OneToOneField(
        OutlineServerKey, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='osk_telegram_user', related_query_name='osk_telegram_user'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def subscription_active(self):
        print(f'AAAA:{self.subscription_expire_datetime}')
        if self.subscription_expire_datetime is None:
            return False
        return self.subscription_expire_datetime > get_now()