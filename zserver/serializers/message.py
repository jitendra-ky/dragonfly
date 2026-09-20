from rest_framework import serializers

from zserver.domain.entities import Message
from zserver.models.message import Message as MessageModel


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        """Configure message validation and response fields."""

        model = MessageModel
        fields = ["id", "sender", "receiver", "content"]

    def to_representation(self, instance: Message | MessageModel) -> dict:
        """Serialize either a domain message or an ORM message."""
        if isinstance(instance, Message):
            return {
                "id": instance.id,
                "sender": instance.sender_id,
                "receiver": instance.receiver_id,
                "content": instance.content,
            }
        return super().to_representation(instance)

    def create(self, validated_data: dict) -> Message:
        """Persist a validated message through the repository context."""
        return self.context["repository"].create(
            sender_id=self.context["sender_id"],
            receiver_id=validated_data["receiver"].pk,
            content=validated_data["content"],
        )
