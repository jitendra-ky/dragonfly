"""Production Django settings for zproject.

Extends common settings with production-specific configuration.
"""

import os
import re
from urllib.parse import parse_qs, unquote, urlparse

from dotenv import load_dotenv

from .settings_common import *  # noqa: F403

# Load environment variables from .env file
load_dotenv()

DEBUG = os.getenv("DJANGO_DEBUG", "false").lower() == "true"

# SECRET_KEY is critical for security and should be set via environment variable in production
SECRET_KEY = os.getenv("SECRET_KEY")

# it only allows request from specified hosts
ALLOWED_HOSTS = ["dragonfly.jitendra.me", os.getenv("WEBSITE_HOSTNAME", "localhost")]
ALLOWED_HOSTS += [
    host.strip()
    for host in os.getenv("ALLOWED_HOSTS", "").split(",")
    if host.strip()
    ]

# it prevent Cross Site Request Forgery (CSRF) attacks
# by specifying trusted origins for secure requests
# stops other websites from tricking your users into sending unsafe request
# usng their logged-in cookies.
CSRF_TRUSTED_ORIGINS = [f"https://{host}" for host in ALLOWED_HOSTS]

# Cross Origin Resource Sharing (CORS) settings for production
# CORS_ALLOWED_ORIGINS specifies which frontend origins
# are allowed to make cross-origin requests to the backend.
CORS_ALLOWED_ORIGINS = [
    host.strip()
    for host in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
    if host.strip()
    ]

# Add WhiteNoiseMiddleware for static file serving
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware", # must be first for WhiteNoise to work properly
    "whitenoise.middleware.WhiteNoiseMiddleware", # serves static files efficiently in production
] + MIDDLEWARE[1:]  # noqa: F405

# Static files storage for production
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

def _database_config_from_url(database_url: str) -> dict:
    """Build Django database settings from a PostgreSQL URL."""
    parsed = urlparse(database_url)
    if not re.match(r"^postgres(?:ql)?(?:\+psycopg2)?$", parsed.scheme):
        raise ValueError("DATABASE_URL must use a PostgreSQL scheme")

    query_params = parse_qs(parsed.query)
    sslmode = query_params.get("sslmode", ["require"])[0]

    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": unquote(parsed.path.lstrip("/")),
        "USER": unquote(parsed.username or ""),
        "PASSWORD": unquote(parsed.password or ""),
        "HOST": parsed.hostname,
        "PORT": parsed.port or "5432",
        "OPTIONS": {
            "sslmode": sslmode,
        },
    }


# PostgreSQL database configuration for production
database_url = os.getenv("DATABASE_URL")

if database_url:
    DATABASES = {"default": _database_config_from_url(database_url)}
else:
    raise RuntimeError("DATABASE_URL must be set in production")

# Static files settings for production
STATIC_ROOT = BASE_DIR / "staticfiles"  # noqa: F405

# Update JWT signing key for production
SIMPLE_JWT["SIGNING_KEY"] = SECRET_KEY  # noqa: F405


# here check everything is setup well if not raise error
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY must be set in production")
if not database_url:
    raise RuntimeError("DATABASE_URL must be set in production")
if not STATIC_ROOT:
    raise RuntimeError("STATIC_ROOT must be set in production")
if not CORS_ALLOWED_ORIGINS:
    raise RuntimeError("CORS_ALLOWED_ORIGINS must be set in production")
