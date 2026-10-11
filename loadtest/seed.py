"""Seed deterministic users and messages for the containerized load test."""

import os
import random
from itertools import cycle

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "zproject.settings")
django.setup()

from django.contrib.auth import get_user_model  # noqa: E402
from django.db import transaction  # noqa: E402

from zchat.models import Message  # noqa: E402

User = get_user_model()
USER_COUNT = 250
MESSAGES_PER_USER = 25
PASSWORD = "LoadtestPassword123!"
EMAIL_TEMPLATE = "loadtest-{index:04d}@example.com"


@transaction.atomic
def seed() -> None:
    users = []
    for index in range(USER_COUNT):
        username = f"loadtest-{index:04d}"
        user, _created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": EMAIL_TEMPLATE.format(index=index),
                "first_name": f"Load Test User {index}",
                "is_active": True,
            },
        )
        user.email = EMAIL_TEMPLATE.format(index=index)
        user.first_name = f"Load Test User {index}"
        user.is_active = True
        user.set_password(PASSWORD)
        users.append(user)
    User.objects.bulk_update(users, ["email", "first_name", "is_active", "password"])

    Message.objects.filter(
        sender__in=users,
        receiver__in=users,
        content__startswith="[loadtest]",
    ).delete()

    random.seed(20261011)
    messages = []
    peer_cycle = cycle(users[1:])
    for sender in users:
        for message_index in range(MESSAGES_PER_USER):
            receiver = next(peer_cycle)
            if receiver == sender:
                receiver = users[(sender.id or 0) % len(users)]
            messages.append(
                Message(
                    sender=sender,
                    receiver=receiver,
                    content=f"[loadtest] message {message_index} from {sender.username}",
                ),
            )
    Message.objects.bulk_create(messages, batch_size=1000)
    print(f"Seeded {len(users)} users and {len(messages)} messages.")
    print(f"Login: {EMAIL_TEMPLATE.format(index=0)} / {PASSWORD}")


if __name__ == "__main__":
    seed()
