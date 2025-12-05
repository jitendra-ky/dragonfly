import os

import django

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "zproject.settings")
# Initialize Django
django.setup()

from zserver.models import User  # noqa: E402


def ensure_active_user_exists():
    """Ensure the active test user exists in the database."""
    email_active = "active_user@jitendra.me"
    password_active = "rootroot"
    if not User.objects.filter(email=email_active).exists():
        User.objects.create_user(
            email=email_active,
            password=password_active,
            contact="1234567890",
            is_active=True,
        )

def ensure_unregistered_user_does_not_exist():
    """Ensure the unregistered test user does not exist in the database."""
    email_unregistered = "unregistered@jitendra.me"
    if User.objects.filter(email=email_unregistered).exists():
        User.objects.filter(email=email_unregistered).delete()

if __name__ == "__main__":
    ensure_active_user_exists()
    ensure_unregistered_user_does_not_exist()
    print("✓ Test users setup completed.")
