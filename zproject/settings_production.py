import os
from pathlib import Path

from dotenv import load_dotenv

from .settings import *  # noqa: F403
from .settings import BASE_DIR, MIDDLEWARE

# Load environment variables
load_dotenv()

# Override specific settings for production
SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.getenv("DJANGO_DEBUG", "false").lower() == "true" # might need to debug in production
ALLOWED_HOSTS = ["dragonfly.jitendra.me", os.getenv("WEBSITE_HOSTNAME", "localhost")]
CSRF_TRUSTED_ORIGINS = ["https://"+ host_name for host_name in ALLOWED_HOSTS]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    *MIDDLEWARE,
]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Parse database connection string from environment variable
db_credentials = {}
for i in os.getenv("DB_CONNECTION_STRING", "").split():
    k, v = i.split("=")
    db_credentials[k.strip()] = v.strip()

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": db_credentials.get("PGDATABASE", ""),
        "USER": db_credentials.get("PGUSER", ""),
        "PASSWORD": db_credentials.get("PGPASSWORD", ""),
        "HOST": db_credentials.get("PGHOST", ""),
        "PORT": db_credentials.get("PGPORT", "5432"),
    },
}

# Static files settings for production
STATIC_ROOT = Path(BASE_DIR) / "staticfiles"
