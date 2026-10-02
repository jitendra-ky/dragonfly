from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, _request: Request) -> Response:
        """Health check endpoint for deployment monitoring."""
        return Response({"status": "healthy"}, status=status.HTTP_200_OK)
