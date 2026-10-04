from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from zchat.models import Message

User = get_user_model()


def create_user(*, contact: str, email: str, **fields: object):
    return User.objects.create_user(
        username=email,
        first_name=contact,
        email=email,
        **fields,
    )


class MessageViewTest(APITestCase):
    def setUp(self):
        """Set up test data for MessageViewTest."""
        self.client = APIClient()
        self.sender = create_user(
            contact="Sender User",
            email="sender_user@jitendra.me",
            password="password123",
            is_active=True,
        )
        self.receiver = create_user(
            contact="Receiver User",
            email="receiver_user@jitendra.me",
            password="password123",
            is_active=True,
        )
        # Generate JWT token for sender
        refresh = RefreshToken.for_user(self.sender)
        self.access_token = str(refresh.access_token)
        self.message_url = reverse("messages")

    def test_send_message(self):
        """Test sending a new message."""
        print("Starting test_send_message")
        data = {
            "receiver": self.receiver.id,
            "content": "Hello, this is a test message.",
        }
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.post(
            self.message_url,
            data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["content"], data["content"])

    def test_retrieve_messages(self):
        """Test retrieving messages between users."""
        print("Starting test_retrieve_messages")
        Message.objects.create(
            sender=self.sender, receiver=self.receiver, content="Test message 1",
        )
        Message.objects.create(
            sender=self.receiver, receiver=self.sender, content="Test message 2",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.get(
            self.message_url,
            HTTP_RECEIVER=str(self.receiver.id),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
