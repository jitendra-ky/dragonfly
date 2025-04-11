import os

from django.shortcuts import render
from django.views import View
from dotenv import load_dotenv
from google.auth.transport import requests
from google.oauth2 import id_token
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from zserver.models import Session, UserProfile
from zserver.serializers import (
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    SessionSerializer,
    SignUpOTPSerializer,
    UserProfileSerializer,
    UnverifiedUserProfileSerializer,
)
from zserver.utils import get_env_var

load_dotenv()

class UserProfileView(APIView):

    def get(self, request: Request) -> Response:
        """Retrieve the profile of the signed-in user."""
        session_id = request.headers.get("session-id")
        if session_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            session = Session.objects.get(session_id=session_id)
        except Session.DoesNotExist:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        user = session.user
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)

    def post(self, request: Request) -> Response:
        """Create a new user profile."""
        serializer = UnverifiedUserProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request: Request) -> Response:
        """Update the profile of the signed-in user."""
        session_id = request.headers.get("session-id")
        if session_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            session = Session.objects.get(session_id=session_id)
        except Session.DoesNotExist:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        user = session.user
        serializer = UserProfileSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request: Request) -> Response:
        """Delete the profile of the signed-in user."""
        session_id = request.headers.get("session-id")
        if session_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            session = Session.objects.get(session_id=session_id)
        except Session.DoesNotExist:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        user = session.user
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SignInView(APIView):

    def get(self, request: Request) -> Response:
        """Retrieve the profile of the signed-in user."""
        session_id = request.headers.get("session-id")
        if session_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            session = Session.objects.get(session_id=session_id)
        except Session.DoesNotExist:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        user = session.user
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)

    def post(self, request: Request) -> Response:
        """Create a new session for the user."""
        serializer = SessionSerializer(data=request.data)
        if serializer.is_valid():
            session = serializer.save()
            return Response({"session_id": session.session_id},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SignUpOTPView(APIView):

    def post(self, request: Request) -> Response:
        """Verify OTP and activate the user."""
        serializer = SignUpOTPSerializer(data=request.data)
        if serializer.is_valid():
            serializer.make_user_verified()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HomeView(View):

    def get(self, request: Request) -> Response:
        """Render the home page."""
        context = {
            "name" : "John Doe",
            "env_var" : get_env_var(),
        }
        return render(request, "home.html", context)

class SignInTemplateView(View):

    def get(self, request: Request) -> Response:
        """Render the sign-in page."""
        context = {
            "title" : "Sign In",
            "env_var" : get_env_var(),
        }
        return render(request, "signin.html", context)


class SignUpTemplateView(View):

    def get(self, request: Request) -> Response:
        """Render the sign-up page."""
        context = {
            "title" : "Sign Up",
            "env_var" : get_env_var,
        }
        return render(request, "signup.html", context)


class ForgotPasswordTemplateView(View):

    def get(self, request: Request) -> Response:
        """Render the forgot password page."""
        context = {
            "title": "Forgot Password",
            "env_var": get_env_var(),
        }
        return render(request, "forgot_password.html", context)


class GoogleLoginView(APIView):

    def post(self, request: Request) -> Response:
        """Handle Google login and create a session for the user."""
        try:
            authorization_code = request.data.get("code")

            # Exchange authorization code for tokens
            tokens = self.exchange_authorization_code(authorization_code)
            print("get the token")

            # Verify the token with Google's API
            google_client_id = os.getenv("GOOGLE_CLIENT_ID")
            id_info = id_token.verify_oauth2_token(tokens["id_token"],
                                                   requests.Request(),
                                                   google_client_id)

            if id_info["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
                return Response({"message": "Invalid issuer"}, status=status.HTTP_403_FORBIDDEN)

            # Get user information
            email = id_info["email"]
            name = id_info.get("name", "")

            # Create or get user
            user, created = UserProfile.objects.get_or_create(
                email=email, defaults={"fullname": name})
            user_session = SessionSerializer().create({"user": user})
            session_id = user_session.session_id

            return Response({"message": "Login successful!",
                             "session_id": session_id},
                            status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def exchange_authorization_code(self, authorization_code: str) -> dict:
        """Exchange the authorization code for tokens."""
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")

        token_request_data = {
            "code": authorization_code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }
        response = requests.requests.post(
            "https://oauth2.googleapis.com/token",
            data=token_request_data,
        )
        response_data = response.json()

        http_success_code = 200
        if response.status_code != http_success_code:
            print("exchange authorization error")
            raise Exception(response_data.get("error",
                                              "Failed to exchange authorization code"))

        return response_data


class ForgotPasswordView(APIView):

    def post(self, request: Request) -> Response:
        """Handle forgot password request."""
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.send_reset_otp()
            return Response({"message": "Password reset OTP sent."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):

    def post(self, request: Request) -> Response:
        """Handle password reset using OTP."""
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.reset_password()
            return Response({"message": "Password reset successful."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
