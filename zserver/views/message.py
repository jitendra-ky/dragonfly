from urllib.request import Request

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from zserver.repositories import MessageRepository, UserRepository
from zserver.serializers.message import MessageSerializer
from zserver.serializers.user_profile import UserProfileSerializer


class MessageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        """Retrieve all messages for the authenticated user."""
        receiver = request.headers.get("receiver")
        if receiver is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
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


class ContactView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        """Retrieve all contacts for the authenticated user."""
        user = request.user
        contacts = UserRepository().get_many(
            MessageRepository().contacts(user_id=user.id),
        )
        # With this one — pass the authenticated user via context for custom field logic
        serializer = UserProfileSerializer(contacts, many=True, context={"user": user})
        return Response(serializer.data)


class AllUsersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, _request: Request) -> Response:
        """Retrieve all users."""
        users = UserRepository().get_many()
        serializer = UserProfileSerializer(users, many=True)
        return Response(serializer.data)
