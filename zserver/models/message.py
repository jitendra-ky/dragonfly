from django.db import models

from zserver.models.user_profile import UserProfile


class Message(models.Model):
    id = models.AutoField(primary_key=True)
    sender = models.ForeignKey(UserProfile, related_name="sent_messages", on_delete=models.CASCADE)
    receiver = models.ForeignKey(
        UserProfile,
        related_name="received_messages",
        on_delete=models.CASCADE,
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        """Return a string representation of the message."""
        return f"Message from {self.sender} to {self.receiver} at {self.timestamp}"
