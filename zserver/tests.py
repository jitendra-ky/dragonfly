from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .models import Session, SignUpOTP, UserProfile


class UserProfileViewTest(TestCase):
    def setUp(self):
        """Set up test data for UserProfileViewTest."""
        # setup mainly do follwing things
        # create 3 users
        # one is not active
        # second is active and has a session
        # thired is active but has no session
        # then it will also make sure that some user not exist
        self.client = APIClient()
        # creating not active user
        self.user = UserProfile.objects.create(
            fullname="not active user",
            email="not_active_user@gmail.com",
            password="password123",
            is_active=False,
        )
        # creating active user with a session
        self.active_user_with_session = UserProfile.objects.create(
            fullname="active user",
            email="active_user@jitenddra.me",
            password="password123",
            is_active=True,
        )
        self.active_user_session = Session.objects.create(
            user=self.active_user_with_session, session_id="session_id",
        )
        # creating active user without session
        self.active_user_without_session = UserProfile.objects.create(
            fullname="active user without session",
            email="active_user_without_session@jitendra.me",
            password="password123",
            is_active=True,
        )
        # not not existed user
        self.not_existed_user = UserProfile(
            fullname="not existed user",
            email="not_existed_user@gmail.com",
            password="password123",
        )
        self.user_url = reverse("user-profile")
        print("_________setup done_________")

    def test_get_user_profile(self):
        """Test retrieving user profile."""
        print("_________test_get_user_profile_________")
        # test get request with session id
        response = self.client.get(
            self.user_url, headers={"session-id": self.active_user_session.session_id},
        )
        print(f"GET response status: {response.status_code}")
        print(f"GET response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.active_user_with_session.email)

        # test get request without session id
        response = self.client.get(self.user_url)
        print(f"GET response status: {response.status_code}")
        print(f"GET response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_user_profile(self):
        """Test creating a new user profile."""
        print("_________test_create_user_profile_________")
        # this will send a post request to create a user that now exists
        new_user = {
            "fullname": self.not_existed_user.fullname,
            "email": self.not_existed_user.email,
            "password": self.not_existed_user.password,
        }
        response = self.client.post(self.user_url, new_user)
        print(f"POST response status: {response.status_code}")
        print(f"POST response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["email"], new_user["email"])
        # now check the user is created and opt is generated
        try:
            user = UserProfile.objects.get(email=new_user["email"])
            print("User created successfully")
        except UserProfile.DoesNotExist:
            self.fail("User not created")
        try:
            otp = SignUpOTP.objects.get(user=user)
            print("OTP generated successfully")
        except SignUpOTP.DoesNotExist:
            self.fail("OTP not generated")

        # this will send a post request to create a user that already exits
        response = self.client.post(self.user_url, new_user)
        print(f"POST response status: {response.status_code}")
        print(f"POST response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["email"][0], "user profile with this email already exists.",
        )

    def test_update_user_profile(self):
        """Test updating an existing user profile."""
        print("_________test_update_user_profile_________")
        # test put request with session id
        updated_user = {
            "fullname": "updated user",
            "email": self.active_user_with_session.email,
            "password": "updated_password",
        }
        response = self.client.put(
            self.user_url,
            updated_user,
            headers={"session-id": self.active_user_session.session_id},
        )
        print(f"PUT response status: {response.status_code}")
        print(f"PUT response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["fullname"], updated_user["fullname"])

        # test put request without session id
        updated_user["fullname"] = "updated user without session id"
        response = self.client.put(self.user_url, updated_user)
        print(f"PUT response status: {response.status_code}")
        print(f"PUT response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_user_profile(self):
        """Test deleting a user profile."""
        print("_________test_delete_user_profile_________")
        # test delete request with session id
        response = self.client.delete(
            self.user_url, headers={"session-id": self.active_user_session.session_id},
        )
        print(f"DELETE response status: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # now check the user is deleted
        try:
            user = UserProfile.objects.get(email=self.active_user_with_session.email)
            self.fail("User not deleted")
        except UserProfile.DoesNotExist:
            print("User deleted successfully")

        # test delete request without session id
        response = self.client.delete(self.user_url)
        print(f"DELETE response status: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # now check the user is not deleted
        try:
            user = UserProfile.objects.get(email=self.active_user_without_session.email)
            print("User not deleted")
        except UserProfile.DoesNotExist:
            print("User not deleted")


class SignInViewTest(TestCase):
    def setUp(self):
        """Set up test data for SignInViewTest."""
        # setup mainly do follwing things
        # create 3 users
        # one is not active
        # second is active and has a session
        # thired is active but has no session
        # then it will also make sure that some user not exist
        self.client = APIClient()
        # creating not active user
        self.user = UserProfile.objects.create(
            fullname="not active user",
            email="not_active_user@gmail.com",
            password="password123",
            is_active=False,
        )
        # creating active user with a session
        self.active_user_with_session = UserProfile.objects.create(
            fullname="active user",
            email="active_user@jitenddra.me",
            password="password123",
            is_active=True,
        )
        self.active_user_session = Session.objects.create(
            user=self.active_user_with_session, session_id="session_id",
        )
        # creating active user without session
        self.active_user_without_session = UserProfile.objects.create(
            fullname="active user without session",
            email="active_user_without_session@jitendra.me",
            password="password123",
            is_active=True,
        )
        # not not existed user
        self.not_existed_user = UserProfile(
            fullname="not existed user",
            email="not_existed_user@gmail.com",
            password="password123",
        )
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
        not_active_user = {"email": self.user.email, "password": self.user.password}
        response = self.client.post(self.user_url, not_active_user)
        print(f"POST response status: {response.status_code}")
        print(f"POST response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["user"][0], "User is not active.")

        # test case for active user with wrong password
        active_user_with_wrong_password = {
            "email": self.active_user_with_session.email,
            "password": "wrong_password",
        }
        response = self.client.post(self.user_url, active_user_with_wrong_password)
        print(f"POST response status: {response.status_code}")
        print(f"POST response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["password"][0], "Incorrect password.")

        # test case for active user with right password
        active_user_with_right_password = {
            "email": self.active_user_with_session.email,
            "password": self.active_user_with_session.password,
        }
        response = self.client.post(self.user_url, active_user_with_right_password)
        print(f"POST response status: {response.status_code}")
        print(f"POST response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("session_id", response.data)
        self.assertEqual(response.data["session_id"], Session.objects.get(session_id=response.data["session_id"]).session_id)

        # test case for not existed user
        not_existed_user = {
            "email": self.not_existed_user.email,
            "password": self.not_existed_user.password,
        }
        response = self.client.post(self.user_url, not_existed_user)
        print(f"POST response status: {response.status_code}")
        print(f"POST response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # self.assertEqual(response.data['email'][0], 'User does not exist.')

    def test_get(self):
        """Test retrieving user profile with session ID."""
        print("_________test_get_________")
        # test get request with valid session id
        response = self.client.get(
            self.user_url, headers={"session-id": self.active_user_session.session_id},
        )
        print(f"GET response status: {response.status_code}")
        print(f"GET response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.active_user_with_session.email)

        # test get request with invalid session id
        response = self.client.get(
            self.user_url, headers={"session-id": "invalid_session_id"},
        )
        print(f"GET response status: {response.status_code}")
        print(f"GET response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # test get request without session id
        response = self.client.get(self.user_url)
        print(f"GET response status: {response.status_code}")
        print(f"GET response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SignUpOTPTest(TestCase):

    def setUp(self):
        """Set up test data for SignUpOTPTest."""
        self.client = APIClient()
        self.endpoint = reverse("sign-up-otp")

        # not not existed user
        self.not_existed_user = UserProfile(
            fullname="not existed user",
            email="not_existed_user@gmail.com",
            password="password123",
        )
        try:
            self.user = UserProfile.objects.get(email=self.not_existed_user.email)
            self.user.delete()
        except UserProfile.DoesNotExist:
            pass

    def test_post(self):
        """Test verifying OTP and activating the user."""
        # first send the post request to create a user on 'user-profile' endpoint
        # then read teh otp from the 'SignUpOTP' model
        # then test the current endpoint by sending post request with the otp

        # create a user
        new_user = {
            "fullname": self.not_existed_user.fullname,
            "email": self.not_existed_user.email,
            "password": self.not_existed_user.password,
        }
        response = self.client.post(reverse("user-profile"), new_user)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # get the otp
        user = UserProfile.objects.get(email=new_user["email"])
        otp = SignUpOTP.objects.get(user=user)
        # test the otp
        data = {"email": new_user["email"], "otp": otp.otp}
        response = self.client.post(self.endpoint, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # now check the user is active
        user = UserProfile.objects.get(email=new_user["email"])
        self.assertTrue(user.is_active)
        # now check the otp is deleted
        try:
            otp = SignUpOTP.objects.get(user=user)
            self.fail("OTP not deleted")
        except SignUpOTP.DoesNotExist:
            print("OTP deleted successfully")
