from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from zserver.serializers import UserDetailSerializer, UserRegisterationSerializer


class UserRegistrationView(generics.CreateAPIView):
    """User registration view."""

    serializer_class = UserRegisterationSerializer
    permission_classes = [AllowAny]


class UserDetailView(APIView):
    """User detail view."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        """Retrieve user details."""
        user = request.user
        serializer = UserDetailSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

