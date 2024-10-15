from datetime import timedelta
from django.utils import timezone


def get_now(utc=None):
    now = timezone.now()
    if utc:
        now = now + timedelta(hours=utc)
    return now
