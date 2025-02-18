from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from zserver.models import Session, SignUpOTP, UserProfile
from zserver.serializers import (
    SessionSerializer,
    SignUpOTPSerializer,
    UserProfileSerializer,
)
from django.shortcuts import render
from django.views import View

from google.oauth2 import id_token
from google.auth.transport import requests

from dotenv import load_dotenv
import os

load_dotenv()

class UserProfileView(APIView):

    def get(self, request: Request) -> Response:
        # only display the signin user's profile
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
        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request: Request) -> Response:
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
        serializer = SessionSerializer(data=request.data)
        if serializer.is_valid():
            session = serializer.save()
            return Response({"session_id": session.session_id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SignUpOTPView(APIView):

    def post(self, request: Request) -> Response:
        serializer = SignUpOTPSerializer(data=request.data)
        if serializer.is_valid():
            serializer.make_user_active()
            serializer.delete_otp()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HomeView(View):
    
    def get(self, request):
        context = {
            "name" : "John Doe",
        }
        return render(request, 'home.html', context)

class SignInTemplateView(View):
    
    def get(self, request):
        context = {
            "title" : "Sign In",
        }
        return render(request, 'signin.html', context)


class SignUpTemplateView(View):
    
    def get(self, request):
        context = {
            "title" : "Sign Up",
        }
        return render(request, 'signup.html', context)


class GoogleLoginView(APIView):
    
    def post(self, request):
        try:
            authorization_code = request.data.get("code")

            # Exchange authorization code for tokens
            tokens = self.exchange_authorization_code(authorization_code)
            print('get the token')

            # Verify the token with Google's API
            GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
            id_info = id_token.verify_oauth2_token(tokens["id_token"], requests.Request(), GOOGLE_CLIENT_ID)

            if id_info["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
                return Response({"message": "Invalid issuer"}, status=status.HTTP_403_FORBIDDEN)

            # Get user information
            email = id_info["email"]
            name = id_info.get("name", "")
            
            # Create or get user
            user, created = UserProfile.objects.get_or_create(email=email, defaults={"fullname": name})
            user_session = SessionSerializer().create({"user": user})
            session_id = user_session.session_id
            
            return Response({"message": "Login successful!", "session_id": session_id}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def exchange_authorization_code(self, authorization_code):
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")

        token_request_data = {
            "code": authorization_code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        }
        response = requests.requests.post('https://oauth2.googleapis.com/token', data=token_request_data)
        response_data = response.json()

        if response.status_code != 200:
            print("exchange authorization error")
            raise Exception(response_data.get("error", "Failed to exchange authorization code"))

        return response_data
