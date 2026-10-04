from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from zchat.repositories import MessageRepository
from zchat.serializers import MessageSerializer


class MessageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        """Retrieve all messages for the authenticated user."""
        receiver = request.headers.get("receiver")
        if receiver is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        MessageRepository().mark_as_read(
            receiver_id=request.user.id,
            sender_id=int(receiver),
        )
        messages = MessageRepository().conversation(
            user_id=request.user.id,
            contact_id=int(receiver),
        )
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    def post(self, request: Request) -> Response:
        """Send a new message."""
        data = request.data.copy()
        serializer = MessageSerializer(
            data=data,
            context={
                "repository": MessageRepository(),
                "sender_id": request.user.id,
            },
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
