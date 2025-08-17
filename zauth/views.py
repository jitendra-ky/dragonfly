from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from zauth.serializers import UserSerializer


class UserView(APIView):
    '''
    GET: Retrieve user information
    POST: Create a new user
    '''
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()]
        else:
            return [IsAuthenticated()]

    def get(self, request, *args, **kwargs):
        # Logic to retrieve user information
        user = request.user
        serializer = self.serializer_class(user)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        # Logic to create a new user
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(self.serializer_class(user).data, status=201)
        return Response(serializer.errors, status=400)
