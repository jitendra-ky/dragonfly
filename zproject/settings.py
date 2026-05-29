"""Main Django settings loader for zproject.

Loads environment-specific settings based on DJANGO_ENV environment variable:
- 'production' or 'prod': Uses settings_prod.py
- 'development' or 'dev' (default): Uses settings_dev.py

Set DJANGO_ENV environment variable to control which settings file is loaded.
"""

import os

from dotenv import load_dotenv

load_dotenv()

# Determine which settings to load based on DJANGO_ENV
DJANGO_ENV = os.getenv("DJANGO_ENV", "development").lower()

if DJANGO_ENV in ("production", "prod"):
    print("*****loading Production setting******")
    from .settings_prod import *  # noqa: F403
else:
    # Default to development
    print("*****loading Development setting******")
    from .settings_dev import *  # noqa: F403
