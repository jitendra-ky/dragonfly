from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.request import Request

class HealthCheckView(APIView):
    """Health check endpoint to verify server status."""
    
    def get(self, request: Request) -> Response:
        """Return a simple health check response."""
        return Response({"status": "ok"}, status=status.HTTP_200_OK)
