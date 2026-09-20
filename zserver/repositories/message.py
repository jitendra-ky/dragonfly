from django.db.models import Q

from zserver.domain.entities import Message
from zserver.models.message import Message as MessageModel


class MessageRepository:
    def create(self, *, sender_id: int, receiver_id: int, content: str) -> Message:
        """Create a message and return its domain representation."""
        message = MessageModel.objects.create(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content,
        )
        return self._to_entity(message)

    def conversation(self, *, user_id: int, contact_id: int) -> list[Message]:
        """Return messages exchanged by two users in chronological order."""
        messages = MessageModel.objects.filter(
            Q(sender_id=user_id, receiver_id=contact_id)
            | Q(sender_id=contact_id, receiver_id=user_id),
        ).order_by("timestamp")
        return [self._to_entity(message) for message in messages]

    def contacts(self, *, user_id: int) -> list[int]:
        """Return the IDs of users who have exchanged messages with a user."""
        sender_ids = MessageModel.objects.filter(sender_id=user_id).values_list(
            "receiver_id", flat=True,
        )
        receiver_ids = MessageModel.objects.filter(receiver_id=user_id).values_list(
            "sender_id", flat=True,
        )
        return list(set(sender_ids).union(receiver_ids))

    @staticmethod
    def _to_entity(message: MessageModel) -> Message:
        return Message(
            id=message.id,
            sender_id=message.sender_id,
            receiver_id=message.receiver_id,
            content=message.content,
            timestamp=message.timestamp,
        )
