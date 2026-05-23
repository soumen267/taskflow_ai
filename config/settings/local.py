"""
Local development settings.
"""
from .base import *  # noqa

DEBUG = True

# Allow all hosts locally
ALLOWED_HOSTS = ["*"]

# Django Debug Toolbar
INSTALLED_APPS += ["debug_toolbar"]  # noqa
MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa

INTERNAL_IPS = ["127.0.0.1"]

# Use simple in-memory cache locally
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Email backend — print to console during development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
