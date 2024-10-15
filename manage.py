import os
import sys

from typing import TypeAlias

from core.config.base import BASE_DIR

_APPS_DIR = BASE_DIR / "core"
_TEMPLATE_DIR = BASE_DIR / "core" / "config" / "__app_template__"

_AppName: TypeAlias = str
_AppDirectory: TypeAlias = str


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
