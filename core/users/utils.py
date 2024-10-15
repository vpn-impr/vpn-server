from core.users.models import User, TelegramUser, get_subscription_trial_date
from django.db import models
from asgiref.sync import sync_to_async


async def update_user(id, **kwargs):
    await TelegramUser.objects.filter(pk=str(id)).aupdate(**kwargs)

async def get_user(telegram_id, username=None, first_name=None, last_name=None):

    if last_name is None:
        last_name = ""

    user, is_new = await TelegramUser.objects.aget_or_create(
        pk=str(telegram_id),
        defaults={
            "subscription_expire_datetime": get_subscription_trial_date(),
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
        },
    )

    if not is_new:
        await update_user(telegram_id, username=username, first_name=first_name, last_name=last_name)

    return user, is_new