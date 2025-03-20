from rest_framework import serializers

from zserver.models.message import Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        """Meta class to specify the model and fields to be serialized."""

        model = Message
        fields = ["id", "sender", "receiver", "content"]
