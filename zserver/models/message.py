from django.conf import settings
from django.db import models


class Message(models.Model):
    id = models.AutoField(primary_key=True)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="sent_messages",
        on_delete=models.CASCADE,
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="received_messages",
        on_delete=models.CASCADE,
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "zserver_message"

    def __str__(self) -> str:
        """Return a string representation of the message."""
        return f"Message from {self.sender} to {self.receiver} at {self.timestamp}"
