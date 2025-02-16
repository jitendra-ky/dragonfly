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