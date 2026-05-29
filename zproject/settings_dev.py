"""Development Django settings for zproject.

Extends common settings with development-specific configuration.
"""

from .settings_common import *  # noqa: F403

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-^k!mmd@-uypekdtuyuj65duylqvj=w-2vhh6y^$be*qzq^+zfu"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

# Database configuration for development (SQLite)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
    },
}

# Update JWT signing key for development
SIMPLE_JWT["SIGNING_KEY"] = SECRET_KEY  # noqa: F405

# CORS Configuration for development
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]
