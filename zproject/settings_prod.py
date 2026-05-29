"""Production Django settings for zproject.

Extends common settings with production-specific configuration.
"""

import os

from dotenv import load_dotenv

from .settings_common import *  # noqa: F403

# Load environment variables from .env file
load_dotenv()

# SECURITY: Override settings for production
SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.getenv("DJANGO_DEBUG", "false").lower() == "true"
ALLOWED_HOSTS = ["dragonfly.jitendra.me", os.getenv("WEBSITE_HOSTNAME", "localhost")]
CSRF_TRUSTED_ORIGINS = ["https://" + host_name for host_name in ALLOWED_HOSTS]

# Add WhiteNoiseMiddleware for static file serving
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
] + MIDDLEWARE[1:]  # noqa: F405

# Static files storage for production
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# PostgreSQL database configuration for production
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "neondb"),
        "USER": os.getenv("DB_USER", "neondb_owner"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT", "5432"),
        "OPTIONS": {
            "sslmode": "require",
        },
    },
}

# Static files settings for production
STATIC_ROOT = BASE_DIR / "staticfiles"  # noqa: F405

# Update JWT signing key for production
SIMPLE_JWT["SIGNING_KEY"] = SECRET_KEY  # noqa: F405

# CORS Configuration for production
CORS_ALLOWED_ORIGINS = [
    "https://dragonfly.jitendra.me",
    os.getenv("FRONTEND_URL", "https://dragonfly.jitendra.me"),
]
