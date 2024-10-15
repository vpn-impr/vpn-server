import os
import django

try:
    _version = (
        os.popen("git describe --tags --dirty --always")  # noqa: S605, S607
        .read()
        .strip()
    )
except Exception:  # noqa: BLE001
    _version = "0.0.0"

__version__ = _version

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.config.settings")
django.setup()
