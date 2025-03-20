from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from zserver.models import Message, Session, UserProfile


class MessageViewTest(APITestCase):
    def setUp(self):
        """Set up test data for MessageViewTest."""
        self.client = APIClient()
        self.sender = UserProfile.objects.create(
            fullname="Sender User",
            email="sender_user@jitendra.me",
            password="password123",
            is_active=True,
        )
        self.receiver = UserProfile.objects.create(
            fullname="Receiver User",
            email="receiver_user@jitendra.me",
            password="password123",
            is_active=True,
        )
        self.session = Session.objects.create(
            user=self.sender, session_id="session_id",
        )
        self.message_url = reverse("messages")

    def test_send_message(self):
        """Test sending a new message."""
        print("Starting test_send_message")
        data = {
            "receiver": self.receiver.id,
            "content": "Hello, this is a test message.",
        }
        response = self.client.post(
            self.message_url,
            data,
            headers={"session-id": self.session.session_id},
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
        response = self.client.get(
            self.message_url,
            headers = {
                "session-id": self.session.session_id,
                "receiver": self.receiver.id,
            })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)


class ContactViewTest(APITestCase):
    def setUp(self):
        """Set up test data for ContactViewTest."""
        self.client = APIClient()
        self.user = UserProfile.objects.create(
            fullname="Test User",
            email="test_user@jitendra.me",
            password="password123",
            is_active=True,
        )
        self.contact = UserProfile.objects.create(
            fullname="Contact User",
            email="contact_user@jitendra.me",
            password="password123",
            is_active=True,
        )
        self.session = Session.objects.create(
            user=self.user, session_id="session_id",
        )
        self.contact_url = reverse("contacts")
        Message.objects.create(
            sender=self.user, receiver=self.contact, content="Hello, contact!",
        )

    def test_retrieve_contacts(self):
        """Test retrieving contacts for the authenticated user."""
        print("Starting test_retrieve_contacts")
        response = self.client.get(
            self.contact_url,
            headers= {
                "session-id": self.session.session_id,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["email"], self.contact.email)


class AllUsersViewTest(APITestCase):
    def setUp(self):
        """Set up test data for AllUsersViewTest."""
        self.client = APIClient()
        self.user1 = UserProfile.objects.create(
            fullname="User One",
            email="user1@jitendra.me",
            password="password123",
            is_active=True,
        )
        self.user2 = UserProfile.objects.create(
            fullname="User Two",
            email="user2@jitendra.me",
            password="password123",
            is_active=True,
        )
        self.all_users_url = reverse("all-users")

    def test_retrieve_all_users(self):
        """Test retrieving all users."""
        print("Starting test_retrieve_all_users")
        response = self.client.get(self.all_users_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["email"], self.user1.email)
        self.assertEqual(response.data[1]["email"], self.user2.email)

