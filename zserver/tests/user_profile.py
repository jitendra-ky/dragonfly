from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from zserver.models import SignUpOTP, UnverifiedUser, VerifyUserOTP

User = get_user_model()


class UserProfileViewTest(TestCase):
    def setUp(self):
        """Set up test data for UserProfileViewTest."""
        # setup mainly do follwing things
        # create 3 users
        # one is not active
        # second is active and has a JWT token
        # third is active but has no token
        # then it will also make sure that some user not exist
        self.client = APIClient()
        # creating not active user
        self.user = User.objects.create_user(
            contact="not active user",
            email="not_active_user@gmail.com",
            password="password123",
            is_active=False,
        )
        # creating active user with JWT token
        self.active_user_with_token = User.objects.create_user(
            contact="active user",
            email="active_user@jitenddra.me",
            password="password123",
            is_active=True,
        )
        refresh = RefreshToken.for_user(self.active_user_with_token)
        self.access_token = str(refresh.access_token)
        # creating active user without token
        self.active_user_without_token = User.objects.create_user(
            contact="active user without token",
            email="active_user_without_token@jitendra.me",
            password="password123",
            is_active=True,
        )
        # not not existed user
        self.not_existed_user_data = {
            "contact": "not existed user",
            "email": "not_existed_user@gmail.com",
            "password": "password123",
        }
        self.user_url = reverse("user-profile")
        print("_________setup done_________")

    def test_get_user_profile(self):
        """Test retrieving user profile."""
        print("_________test_get_user_profile_________")
        # test get request with JWT token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.get(self.user_url)
        print(f"GET response status: {response.status_code}")
        print(f"GET response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.active_user_with_token.email)

        # test get request without JWT token
        self.client.credentials()  # Clear credentials
        response = self.client.get(self.user_url)
        print(f"GET response status: {response.status_code}")
        print(f"GET response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_user_profile(self):
        """Test creating a new user profile."""
        print("_________test_create_user_profile_________")
        # Clear any existing credentials for signup (should be public)
        self.client.credentials()
        # this will send a post request to create a user that now exists
        new_user = {
            "contact": self.not_existed_user_data["contact"],
            "email": self.not_existed_user_data["email"],
            "password": self.not_existed_user_data["password"],
        }
        response = self.client.post(self.user_url, new_user)
        print(f"POST response status: {response.status_code}")
        print(f"POST response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["email"], new_user["email"])
        # now check the user is created and opt is generated
        try:
            user = UnverifiedUser.objects.get(email=new_user["email"])
            print("User created successfully")
        except UnverifiedUser.DoesNotExist:
            self.fail("User not created")
        try:
            VerifyUserOTP.objects.get(user=user)
            print("OTP generated successfully")
        except VerifyUserOTP.DoesNotExist:
            self.fail("OTP not generated")

        # this will send a post request to create a user that already exits
        existed_user = {
            "contact": self.active_user_without_token.contact,
            "email": self.active_user_without_token.email,
            "password": "somepassword",
        }
        response = self.client.post(self.user_url, existed_user)
        print(f"POST response status: {response.status_code}")
        print(f"POST response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["email"][0],
            "Email is already in use.",
        )

    def test_update_user_profile(self):
        """Test updating an existing user profile."""
        print("_________test_update_user_profile_________")
        # test put request with JWT token
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
        print(f"PUT response status: {response.status_code}")
        print(f"PUT response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["contact"], updated_user["contact"])

        # test put request without JWT token
        self.client.credentials()  # Clear credentials
        updated_user["contact"] = "updated user without token"
        response = self.client.put(self.user_url, updated_user)
        print(f"PUT response status: {response.status_code}")
        print(f"PUT response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_user_profile(self):
        """Test deleting a user profile."""
        print("_________test_delete_user_profile_________")
        # test delete request with JWT token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.delete(self.user_url)
        print(f"DELETE response status: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # now check the user is deleted
        try:
            User.objects.get(email=self.active_user_with_token.email)
            self.fail("User not deleted")
        except User.DoesNotExist:
            print("User deleted successfully")

        # test delete request without JWT token
        self.client.credentials()  # Clear credentials
        response = self.client.delete(self.user_url)
        print(f"DELETE response status: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # now check the user is not deleted
        try:
            User.objects.get(email=self.active_user_without_token.email)
            print("✓ user not deleted")
        except User.DoesNotExist:
            self.fail("✕ User deleted without JWT token")


class SignInViewTest(TestCase):
    def setUp(self):
        """Set up test data for SignInViewTest."""
        # setup mainly do follwing things
        # create 3 users
        # one is not active
        # second is active and has a JWT token
        # third is active but has no token
        # then it will also make sure that some user not exist
        self.client = APIClient()
        # creating not active user
        self.user = User.objects.create_user(
            contact="not active user",
            email="not_active_user@gmail.com",
            password="password123",
            is_active=False,
        )
        # creating active user with JWT token
        self.active_user_with_token = User.objects.create_user(
            contact="active user",
            email="active_user@jitenddra.me",
            password="password123",
            is_active=True,
        )
        refresh = RefreshToken.for_user(self.active_user_with_token)
        self.access_token = str(refresh.access_token)
        # creating active user without token
        self.active_user_without_token = User.objects.create_user(
            contact="active user without token",
            email="active_user_without_token@jitendra.me",
            password="password123",
            is_active=True,
        )
        # not not existed user
        self.not_existed_user_data = {
            "contact": "not existed user",
            "email": "not_existed_user@gmail.com",
            "password": "password123",
        }
        self.user_url = reverse("sign-in")
        print("_________setup done_________")

    def test_post(self):
        """Test creating a new session for the user."""
        print("_________test_post_________")
        # here we write test cases for all different type of user
        # our test inluce for
        # not active user with right password
        # active user with wrong password
        # active user with right password
        # not existed user

        # test case for not active user
        not_active_user = {"email": self.user.email, "password": "password123"}
        response = self.client.post(self.user_url, not_active_user)
        print(f"POST response status: {response.status_code}")
        print(f"POST response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["user"][0], "User is not active.")

        # test case for active user with wrong password
        active_user_with_wrong_password = {
            "email": self.active_user_with_token.email,
            "password": "wrong_password",
        }
        response = self.client.post(self.user_url, active_user_with_wrong_password)
        print(f"POST response status: {response.status_code}")
        print(f"POST response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["password"][0], "Incorrect password.")

        # test case for active user with right password
        active_user_with_right_password = {
            "email": self.active_user_with_token.email,
            "password": "password123",  # Use the correct password
        }
        response = self.client.post(self.user_url, active_user_with_right_password)
        print(f"POST response status: {response.status_code}")
        print(f"POST response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("user", response.data)

        # test case for not existed user
        not_existed_user = {
            "email": self.not_existed_user_data["email"],
            "password": self.not_existed_user_data["password"],
        }
        response = self.client.post(self.user_url, not_existed_user)
        print(f"POST response status: {response.status_code}")
        print(f"POST response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["email"][0], "User does not exist.")

    def test_get(self):
        """Test retrieving user profile with JWT token."""
        print("_________test_get_________")
        # test get request with valid JWT token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.get(self.user_url)
        print(f"GET response status: {response.status_code}")
        print(f"GET response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.active_user_with_token.email)

        # test get request with invalid JWT token
        self.client.credentials(HTTP_AUTHORIZATION="Bearer invalid_token")
        response = self.client.get(self.user_url)
        print(f"GET response status: {response.status_code}")
        print(f"GET response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # test get request without JWT token
        self.client.credentials()  # Clear credentials
        response = self.client.get(self.user_url)
        print(f"GET response status: {response.status_code}")
        print(f"GET response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class VerifyUserOTPTest(TestCase):

    def setUp(self):
        """Set up test data for SignUpOTPTest."""
        self.client = APIClient()
        self.endpoint = reverse("sign-up-otp")

        # not not existed user
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
        # first send the post request to create a user on 'user-profile' endpoint
        # then read teh otp from the 'VerifyUserOTP' model
        # then test the current endpoint by sending post request with the otp

        # create a user
        new_user = {
            "contact": self.not_existed_user_data["contact"],
            "email": self.not_existed_user_data["email"],
            "password": self.not_existed_user_data["password"],
        }
        response = self.client.post(reverse("user-profile"), new_user)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # get the otp
        user = UnverifiedUser.objects.get(email=new_user["email"])
        otp = VerifyUserOTP.objects.get(user=user)
        # test the otp
        data = {"email": new_user["email"], "otp": otp.otp}
        response = self.client.post(self.endpoint, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify JWT tokens are returned
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("user", response.data)
        # now check the user is active
        user = User.objects.get(email=new_user["email"])
        self.assertTrue(user.is_active)
        # now check the otp is deleted
        try:
            otp = SignUpOTP.objects.get(user=user)
            self.fail("OTP not deleted")
        except SignUpOTP.DoesNotExist:
            print("OTP deleted successfully")


class ForgotPasswordViewTest(TestCase):
    def setUp(self):
        """Set up test data for ForgotPasswordViewTest."""
        self.active_user = User.objects.create_user(
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

        # Create a user and generate OTP
        self.user = User.objects.create_user(
            contact="Test User",
            email="test_user@jitendra.me",
            password="oldpassword",
            is_active=True,
        )
        self.user.generate_otp()
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

        # Verify the password is updated using check_password
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
