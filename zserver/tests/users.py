import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserRegistrationViewTest(TestCase):
    """Test cases for UserRegistrationView."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.registration_url = reverse("v2_user_registration")
        self.valid_user_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpassword123",
        }

    def test_user_registration_success(self):
        """Test successful user registration."""
        response = self.client.post(
            self.registration_url,
            data=json.dumps(self.valid_user_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="testuser").exists())

        response_data = response.json()
        self.assertEqual(response_data["username"], "testuser")
        self.assertEqual(response_data["email"], "testuser@example.com")
        self.assertNotIn("password", response_data)

    def test_user_registration_validation_error(self):
        """Test user registration with invalid data."""
        invalid_data = {
            "email": "testuser@example.com",
            "password": "testpassword123",
            # Missing username
        }

        response = self.client.post(
            self.registration_url,
            data=json.dumps(invalid_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserDetailViewTest(TestCase):
    """Test cases for UserDetailView."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user_detail_url = reverse("v2_user_detail")

        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword123",
        )

        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

    def test_get_user_detail_success(self):
        """Test successful retrieval of user details."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        response = self.client.get(self.user_detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()

        self.assertEqual(response_data["username"], "testuser")
        self.assertEqual(response_data["email"], "testuser@example.com")
        self.assertNotIn("password", response_data)

    def test_get_user_detail_without_authentication(self):
        """Test access without authentication token."""
        response = self.client.get(self.user_detail_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
