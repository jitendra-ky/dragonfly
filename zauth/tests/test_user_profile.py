from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from zauth.models import SignUpOTP, VerifyUserOTP
from zchat.models import Message

User = get_user_model()


def create_user(*, contact: str, email: str, **fields):
    return User.objects.create_user(
        username=email,
        first_name=contact,
        email=email,
        **fields,
    )


class UserProfileViewTest(TestCase):
    def setUp(self):
        """Set up test data for UserProfileViewTest."""
        self.client = APIClient()
        self.user = create_user(
            contact="not active user",
            email="not_active_user@gmail.com",
            password="password123",
            is_active=False,
        )
        self.active_user_with_token = create_user(
            contact="active user",
            email="active_user@jitenddra.me",
            password="password123",
            is_active=True,
        )
        refresh = RefreshToken.for_user(self.active_user_with_token)
        self.access_token = str(refresh.access_token)
        self.active_user_without_token = create_user(
            contact="active user without token",
            email="active_user_without_token@jitendra.me",
            password="password123",
            is_active=True,
        )
        self.not_existed_user_data = {
            "contact": "not existed user",
            "email": "not_existed_user@gmail.com",
            "password": "password123",
        }
        self.user_url = reverse("user-profile")

    def test_get_user_profile(self):
        """Test retrieving user profile."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.get(self.user_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.active_user_with_token.email)

        self.client.credentials()  # Clear credentials
        response = self.client.get(self.user_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_user_profile(self):
        """Test creating a new user profile."""
        self.client.credentials()
        new_user = {
            "contact": self.not_existed_user_data["contact"],
            "email": self.not_existed_user_data["email"],
            "password": self.not_existed_user_data["password"],
        }
        response = self.client.post(self.user_url, new_user)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["email"], new_user["email"])
        try:
            user = User.objects.get(username=new_user["email"], is_active=False)
        except User.DoesNotExist:
            self.fail("User not created")
        try:
            VerifyUserOTP.objects.get(user=user)
        except VerifyUserOTP.DoesNotExist:
            self.fail("OTP not generated")

        existed_user = {
            "contact": self.active_user_without_token.first_name,
            "email": self.active_user_without_token.email,
            "password": "somepassword",
        }
        response = self.client.post(self.user_url, existed_user)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["email"][0],
            "Email is already in use.",
        )

    def test_update_user_profile(self):
        """Test updating an existing user profile."""
        updated_user = {
            "contact": "updated user",
            "email": self.active_user_with_token.email,
            "password": "updated_password",
        }
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.put(
            self.user_url,
            updated_user,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["contact"], updated_user["contact"])

        self.client.credentials()
        updated_user["contact"] = "updated user without token"
        response = self.client.put(self.user_url, updated_user)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_user_profile(self):
        """Test deleting a user profile."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.delete(self.user_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        try:
            User.objects.get(email=self.active_user_with_token.email)
            self.fail("User not deleted")
        except User.DoesNotExist:
            pass

        self.client.credentials()
        response = self.client.delete(self.user_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        try:
            User.objects.get(email=self.active_user_without_token.email)
        except User.DoesNotExist:
            self.fail("User deleted without JWT token")


class SignInViewTest(TestCase):
    def setUp(self):
        """Set up test data for SignInViewTest."""
        self.client = APIClient()
        self.user = create_user(
            contact="not active user",
            email="not_active_user@gmail.com",
            password="password123",
            is_active=False,
        )
        self.active_user_with_token = create_user(
            contact="active user",
            email="active_user@jitenddra.me",
            password="password123",
            is_active=True,
        )
        refresh = RefreshToken.for_user(self.active_user_with_token)
        self.access_token = str(refresh.access_token)
        self.active_user_without_token = create_user(
            contact="active user without token",
            email="active_user_without_token@jitendra.me",
            password="password123",
            is_active=True,
        )
        self.not_existed_user_data = {
            "contact": "not existed user",
            "email": "not_existed_user@gmail.com",
            "password": "password123",
        }
        self.user_url = reverse("sign-in")

    def test_post(self):
        """Test creating a new session for the user."""
        not_active_user = {"email": self.user.email, "password": "password123"}
        response = self.client.post(self.user_url, not_active_user)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["user"][0], "User is not active.")

        active_user_with_wrong_password = {
            "email": self.active_user_with_token.email,
            "password": "wrong_password",
        }
        response = self.client.post(self.user_url, active_user_with_wrong_password)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["password"][0], "Incorrect password.")

        active_user_with_right_password = {
            "email": self.active_user_with_token.email,
            "password": "password123",
        }
        response = self.client.post(self.user_url, active_user_with_right_password)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("user", response.data)

        not_existed_user = {
            "email": self.not_existed_user_data["email"],
            "password": self.not_existed_user_data["password"],
        }
        response = self.client.post(self.user_url, not_existed_user)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["email"][0], "User does not exist.")

    def test_get(self):
        """Test retrieving user profile with JWT token."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.get(self.user_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.active_user_with_token.email)

        self.client.credentials(HTTP_AUTHORIZATION="Bearer invalid_token")
        response = self.client.get(self.user_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.credentials()
        response = self.client.get(self.user_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class VerifyUserOTPTest(TestCase):
    def setUp(self):
        """Set up test data for VerifyUserOTPTest."""
        self.client = APIClient()
        self.endpoint = reverse("sign-up-otp")

        self.not_existed_user_data = {
            "contact": "not existed user",
            "email": "not_existed_user@gmail.com",
            "password": "password123",
        }
        try:
            user = User.objects.get(email=self.not_existed_user_data["email"])
            user.delete()
        except User.DoesNotExist:
            pass

    def test_post(self):
        """Test verifying OTP and activating the user."""
        new_user = {
            "contact": self.not_existed_user_data["contact"],
            "email": self.not_existed_user_data["email"],
            "password": self.not_existed_user_data["password"],
        }
        response = self.client.post(reverse("user-profile"), new_user)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(username=new_user["email"], is_active=False)
        otp = VerifyUserOTP.objects.get(user=user)

        data = {"email": new_user["email"], "otp": otp.otp}
        response = self.client.post(self.endpoint, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("user", response.data)

        user = User.objects.get(email=new_user["email"])
        self.assertTrue(user.is_active)
        try:
            SignUpOTP.objects.get(user=user)
            self.fail("OTP not deleted")
        except SignUpOTP.DoesNotExist:
            pass


class ForgotPasswordViewTest(TestCase):
    def setUp(self):
        """Set up test data for ForgotPasswordViewTest."""
        self.active_user = create_user(
            contact="Test User",
            email="test_user@jitendra.me",
            password="rootrootroot",
            is_active=True,
        )
        self.client = APIClient()
        self.url = reverse("forgot-password")

    def test_forgot_password_valid_email(self):
        """Test forgot password with a valid email."""
        response = self.client.post(self.url, {"email": self.active_user.email})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Password reset OTP sent.")


class ResetPasswordViewTest(TestCase):
    def setUp(self):
        """Set up test data for ResetPasswordViewTest."""
        self.client = APIClient()
        self.url = reverse("reset-password")

        self.user = create_user(
            contact="Test User",
            email="test_user@jitendra.me",
            password="oldpassword",
            is_active=True,
        )
        SignUpOTP.objects.create(user=self.user, otp="123456")
        self.otp = SignUpOTP.objects.get(user=self.user).otp

    def test_reset_password_valid_otp(self):
        """Test resetting password with a valid OTP."""
        data = {
            "email": self.user.email,
            "otp": self.otp,
            "new_password": "newpassword123",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Password reset successful.")

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpassword123"))

    def test_reset_password_invalid_otp(self):
        """Test resetting password with an invalid OTP."""
        data = {
            "email": self.user.email,
            "otp": "000000",
            "new_password": "newpassword123",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["otp"][0], "Incorrect OTP.")

    def test_reset_password_nonexistent_user(self):
        """Test resetting password for a nonexistent user."""
        data = {
            "email": "nonexistent@jitendra.me",
            "otp": self.otp,
            "new_password": "newpassword123",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["email"][0], "User does not exist.")


class ContactViewTest(TestCase):
    def setUp(self):
        """Set up test data for ContactViewTest."""
        self.client = APIClient()
        self.user = create_user(
            contact="Test User",
            email="test_user@jitendra.me",
            password="password123",
            is_active=True,
        )
        self.contact = create_user(
            contact="Contact User",
            email="contact_user@jitendra.me",
            password="password123",
            is_active=True,
        )
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.contact_url = reverse("contacts")
        Message.objects.create(
            sender=self.user, receiver=self.contact, content="Hello, contact!",
        )

    def test_retrieve_contacts(self):
        """Test retrieving contacts for the authenticated user."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.get(
            self.contact_url,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["email"], self.contact.email)


class AllUsersViewTest(TestCase):
    def setUp(self):
        """Set up test data for AllUsersViewTest."""
        self.client = APIClient()
        self.user1 = create_user(
            contact="User One",
            email="user1@jitendra.me",
            password="password123",
            is_active=True,
        )
        self.user2 = create_user(
            contact="User Two",
            email="user2@jitendra.me",
            password="password123",
            is_active=True,
        )
        refresh = RefreshToken.for_user(self.user1)
        self.access_token = str(refresh.access_token)
        self.all_users_url = reverse("all-users")

    def test_retrieve_all_users(self):
        """Test retrieving all users."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.get(self.all_users_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["email"], self.user1.email)
        self.assertEqual(response.data[1]["email"], self.user2.email)
