import os

from django.core.wsgi import get_wsgi_application
from dotenv import load_dotenv

load_dotenv()

# Force-set DJANGO_SETTINGS_MODULE before initializing Django
if os.getenv("DJANGO_PRODUCTION", "").lower() == "true":
    os.environ["DJANGO_SETTINGS_MODULE"] = "zproject.settings_production"
else:
    os.environ["DJANGO_SETTINGS_MODULE"] = "zproject.settings"

application = get_wsgi_application()
