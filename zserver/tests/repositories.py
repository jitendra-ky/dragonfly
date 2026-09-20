from django.contrib.auth import get_user_model
from django.test import TestCase

from zserver.domain.entities import Message as MessageEntity
from zserver.domain.entities import User as UserEntity
from zserver.models import VerifyUserOTP
from zserver.repositories import MessageRepository, UserRepository, VerificationRepository

User = get_user_model()


def create_user(*, contact: str, email: str, **fields):
    return User.objects.create_user(
        username=email,
        first_name=contact,
        email=email,
        **fields,
    )


class RepositoryTest(TestCase):
    def setUp(self) -> None:
        """Create users used by repository tests."""
        self.sender = create_user(
            email="sender@example.com",
            contact="Sender",
            password="password123",
            is_active=True,
        )
        self.receiver = create_user(
            email="receiver@example.com",
            contact="Receiver",
            password="password123",
            is_active=True,
        )
        self.message_repository = MessageRepository()
        self.user_repository = UserRepository()
        self.verification_repository = VerificationRepository()

    def test_user_repository_returns_domain_entities(self) -> None:
        """Repository results are domain users rather than ORM models."""
        users = self.user_repository.get_many()

        self.assertTrue(all(isinstance(user, UserEntity) for user in users))
        self.assertEqual({user.id for user in users}, {self.sender.id, self.receiver.id})

    def test_user_repository_finds_users_by_email(self) -> None:
        """Authentication lookup is owned by the user repository."""
        user = self.user_repository.get_by_email(self.sender.email)

        self.assertEqual(user.id, self.sender.id)
        self.assertTrue(self.user_repository.email_exists(self.sender.email))
        self.assertFalse(self.user_repository.email_exists("missing@example.com"))

    def test_message_repository_creates_and_reads_conversation(self) -> None:
        """Repository message writes can be read in either direction."""
        message = self.message_repository.create(
            sender_id=self.sender.id,
            receiver_id=self.receiver.id,
            content="Hello",
        )

        conversation = self.message_repository.conversation(
            user_id=self.receiver.id,
            contact_id=self.sender.id,
        )

        self.assertIsInstance(message, MessageEntity)
        self.assertEqual(len(conversation), 1)
        self.assertEqual(conversation[0].content, "Hello")

    def test_verification_repository_creates_pending_signup(self) -> None:
        """Pending signup creation also creates its verification OTP."""
        user = self.verification_repository.create_unverified_user(
            email="pending@example.com",
            contact="Pending",
            password="hashed-password",
        )

        otp = self.verification_repository.get_verification_otp(user)

        self.assertIsInstance(otp, VerifyUserOTP)
        self.assertEqual(len(otp.otp), 6)

    def test_message_repository_returns_unique_contacts(self) -> None:
        """Contact lookup returns each conversation partner once."""
        self.message_repository.create(
            sender_id=self.sender.id,
            receiver_id=self.receiver.id,
            content="First",
        )
        self.message_repository.create(
            sender_id=self.receiver.id,
            receiver_id=self.sender.id,
            content="Second",
        )

        contacts = self.message_repository.contacts(user_id=self.sender.id)

        self.assertEqual(contacts, [self.receiver.id])
