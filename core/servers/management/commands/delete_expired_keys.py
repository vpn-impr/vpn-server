import time
from datetime import timedelta
import requests
from django.core.management.base import BaseCommand
from core.users.models import TelegramUser
from core.utils.datetimes import get_now

from bot.config.bot import TELEGRAM_API_TOKEN

import logging
logger = logging.getLogger(__name__)

url = f"https://api.telegram.org/bot{TELEGRAM_API_TOKEN}/sendMessage"

class Command(BaseCommand):
    help = 'Runs Delete Expired Keys'

    def handle(self, *args, **kwargs):
        while True:
            try:
                now = get_now() + timedelta(hours=1)
                users = TelegramUser.objects.filter(subscription_expire_datetime__lte=now, outline_server_key__isnull=False)
                for user in users:
                    user.outline_server_key.delete()
                    logger.info(f'USER {user.id}: Deleted Server Key')
                    payload = {
                        'chat_id': user.id,
                        'text': f'Срок подписки истек'
                    }
                    response = requests.post(url, data=payload)
                    response.raise_for_status()
                time.sleep(60)
            except Exception as e:
                logger.exception(str(e))
