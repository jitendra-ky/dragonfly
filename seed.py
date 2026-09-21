# -*- coding: utf-8 -*-
"""
Seed script -- creates 5 users and some messages between them.
Run with:  .venv\\Scripts\\python.exe seed.py
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "zproject.settings")
django.setup()

from django.contrib.auth import get_user_model
from zserver.models.message import Message

User = get_user_model()

# -- Users --------------------------------------------------------------------

USERS = [
    {"username": "alice", "email": "alice@example.com", "first_name": "Alice", "last_name": "Smith"},
    {"username": "bob",   "email": "bob@example.com",   "first_name": "Bob",   "last_name": "Johnson"},
    {"username": "carol", "email": "carol@example.com", "first_name": "Carol", "last_name": "Williams"},
    {"username": "dave",  "email": "dave@example.com",  "first_name": "Dave",  "last_name": "Brown"},
    {"username": "eve",   "email": "eve@example.com",   "first_name": "Eve",   "last_name": "Davis"},
]

PASSWORD = "password123"

created_users = {}
for data in USERS:
    user, created = User.objects.get_or_create(
        username=data["username"],
        defaults={
            "email":      data["email"],
            "first_name": data["first_name"],
            "last_name":  data["last_name"],
            "is_active":  True,
        },
    )
    if created:
        user.set_password(PASSWORD)
        user.save()
        print(f"  [+] Created user: {user.username}")
    else:
        print(f"  [~] User already exists: {user.username}")

    created_users[data["username"]] = user

alice, bob, carol, dave, eve = (
    created_users["alice"],
    created_users["bob"],
    created_users["carol"],
    created_users["dave"],
    created_users["eve"],
)

# -- Messages -----------------------------------------------------------------

MESSAGES = [
    # Alice <-> Bob
    (alice, bob,   "Hey Bob, how's it going?"),
    (bob,   alice, "Hey Alice! All good, you?"),
    (alice, bob,   "Pretty good, thanks! Are you joining the call later?"),
    (bob,   alice, "Yeah, I'll be there at 3pm."),

    # Alice <-> Carol
    (alice, carol, "Carol, did you see the new designs?"),
    (carol, alice, "Just saw them -- they look great!"),
    (alice, carol, "Right? The team did an amazing job."),

    # Bob <-> Dave
    (bob,  dave, "Dave, can you review my PR when you get a chance?"),
    (dave, bob,  "Sure, sending feedback in a few minutes."),
    (bob,  dave, "Awesome, thank you!"),

    # Carol <-> Eve
    (carol, eve, "Eve, are you free for lunch tomorrow?"),
    (eve,  carol, "Yes! Let's meet at noon."),
    (carol, eve,  "Perfect, see you then :)"),

    # Dave <-> Eve
    (dave, eve, "Eve, the deployment is done."),
    (eve,  dave, "Nice work! Everything looks stable."),

    # Alice <-> Eve
    (alice, eve,  "Eve, Bob mentioned you're handling the release notes?"),
    (eve,  alice, "That's right, I'll share a draft by EOD."),
    (alice, eve,  "Great, ping me once it's ready."),
]

# Clear previously seeded messages to avoid duplicates on re-runs
print("\nClearing existing seed messages...")
usernames = [u["username"] for u in USERS]
users = list(created_users.values())
deleted, _ = Message.objects.filter(sender__in=users, receiver__in=users).delete()
print(f"  Deleted {deleted} existing message(s).")

print("\nSeeding messages...")
for sender, receiver, content in MESSAGES:
    Message.objects.create(sender=sender, receiver=receiver, content=content)
    print(f"  [+] {sender.username} -> {receiver.username}: {content[:55]}")

print(f"\nDone. {len(MESSAGES)} messages seeded.")
print(f"All users share the password: '{PASSWORD}'")

