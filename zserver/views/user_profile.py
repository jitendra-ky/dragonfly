import os

from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.views import View
from dotenv import load_dotenv
from google.auth.transport import requests
from google.oauth2 import id_token
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from zserver.serializers import (
    ForgotPasswordSerializer,
    LoginSerializer,
    ResetPasswordSerializer,
    UnverifiedUserProfileSerializer,
    UserProfileSerializer,
    VerifyUserOTPSerializer,
)
from zserver.utils import get_env_var

load_dotenv()

User = get_user_model()

class UserProfileView(APIView):
    
    def get_permissions(self):
        """
        Instantiate and return the list of permissions that this view requires.
        POST (signup) is public, other methods require authentication.
        """
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request: Request) -> Response:
        """Retrieve the profile of the signed-in user."""
        serializer = UserProfileSerializer(request.user)
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
        serializer = UserProfileSerializer(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request: Request) -> Response:
        """Delete the profile of the signed-in user."""
        request.user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SignInView(APIView):
    
    def get_permissions(self):
        """
        GET requires authentication, POST (login) is public.
        """
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [AllowAny()]

    def get(self, request: Request) -> Response:
        """Retrieve the profile of the signed-in user."""
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def post(self, request: Request) -> Response:
        """Authenticate user and return JWT tokens."""
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            tokens = serializer.get_tokens()
            return Response(tokens, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyUserOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        """Verify OTP, signup user, and return JWT tokens."""
        serializer = VerifyUserOTPSerializer(data=request.data)
        if serializer.is_valid():
            tokens = serializer.signup_user()
            return Response(tokens, status=status.HTTP_200_OK)
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
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        """Handle Google login and return JWT tokens for the user."""
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
            user, created = User.objects.get_or_create(
                email=email,
                defaults={"contact": name, "is_active": True, "email_verified": True}
            )
            # For Google OAuth users, set unusable password
            if created:
                user.set_unusable_password()
                user.save()
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                "message": "Login successful!",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "contact": user.contact,
                }
            }, status=status.HTTP_200_OK)

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
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        """Handle forgot password request."""
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.send_reset_otp()
            return Response({"message": "Password reset OTP sent."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        """Handle password reset using OTP."""
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.reset_password()
            return Response({"message": "Password reset successful."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
