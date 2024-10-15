import logging
from os import getenv

logger = logging.getLogger(__name__)

_default_secret_key = "your-super-secret-and-long-django-secret-key"  # noqa: S105
SECRET_KEY = getenv("DJANGO_SECRET_KEY", _default_secret_key)

if _default_secret_key == SECRET_KEY:
    logger.warning("You are using a default Django secret key")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = getenv("DJANGO_DEBUG", "true").lower() == "true"

ALLOWED_HOSTS = [
    host.strip() for host in getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")
]

CSRF_TRUSTED_ORIGINS = [
    host.strip() for host in getenv("CSRF_TRUSTED_ORIGINS", "http://localhost").split(",")
]

CORS_ALLOW_ALL_ORIGINS = getenv("CORS_ALLOW_ALL_ORIGINS", "true").lower() == "true"
CORS_ALLOW_CREDENTIALS = getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
CORS_ALLOWED_ORIGINS = getenv("CORS_ALLOWED_ORIGINS", "http://localhost").split(
    ",",
)
CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
    "HEAD"
]

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "origin",
    "dnt",
    "user-agent",
    "x-csrftoken",
    "csrftoken",
    "x-requested-with",
    "organisation-slug",
    "access-control-allow-origin"
]
