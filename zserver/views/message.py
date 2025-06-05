from urllib.request import Request

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from zserver.models import Message, Session, UserProfile
from zserver.serializers.message import MessageSerializer
from zserver.serializers.user_profile import UserProfileSerializer


class MessageView(APIView):

    def get(self, request: Request) -> Response:
        """Retrieve all messages for the authenticated user."""
        session_id = request.headers.get("session-id")
        if session_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            session = Session.objects.get(session_id=session_id)
        except Session.DoesNotExist:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        user = session.user

        receiver = request.headers.get("receiver")
        if receiver is not None:
            messages_send = Message.objects.filter(sender=user, receiver=int(receiver))
            messages_receive = Message.objects.filter(sender=int(receiver), receiver=user)
            messages = messages_send.union(messages_receive).order_by("timestamp")
        else:
            return Response(status=status.HTTP_400_BAD)
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    def post(self, request: Request) -> Response:
        """Send a new message."""
        session_id = request.headers.get("session-id")
        if session_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            session = Session.objects.get(session_id=session_id)
        except Session.DoesNotExist:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        user = session.user

        data = request.data.copy()
        data["sender"] = user.id
        serializer = MessageSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContactView(APIView):

    def get(self, request: Request) -> Response:
        """Retrieve all contacts for the authenticated user."""
        session_id = request.headers.get("session-id")
        if session_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            session = Session.objects.get(session_id=session_id)
        except Session.DoesNotExist:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        user = session.user
        contacts_sender = { msg.receiver for msg in Message.objects.filter(sender=user) }
        contacts_receiver = { msg.sender for msg in Message.objects.filter(receiver=user) }
        contacts = contacts_sender.union(contacts_receiver)
        # With this one — pass the authenticated user via context for custom field logic
        serializer = UserProfileSerializer(contacts, many=True, context={"user": user})
        return Response(serializer.data)


class AllUsersView(APIView):

    def get(self, request: Request) -> Response:
        """Retrieve all users."""
        print(request.headers)
        users = UserProfile.objects.all()
        serializer = UserProfileSerializer(users, many=True)
        return Response(serializer.data)
