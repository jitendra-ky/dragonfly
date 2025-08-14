from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

class TokenObtainPairViewTest(APITestCase):
    def test_token_obtain_pair(self):
        # Create a user
        from django.contrib.auth.models import User
        user = User.objects.create_user(username='testuser', password='testpass123')
        url = reverse('auth_token_obtain_pair')
        data = {'username': 'testuser', 'password': 'testpass123'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

class TokenRefreshViewTest(APITestCase):
    def test_token_refresh(self):
        from django.contrib.auth.models import User
        user = User.objects.create_user(username='testuser', password='testpass123')
        obtain_url = reverse('auth_token_obtain_pair')
        obtain_data = {'username': 'testuser', 'password': 'testpass123'}
        obtain_response = self.client.post(obtain_url, obtain_data)
        refresh_token = obtain_response.data['refresh']
        refresh_url = reverse('auth_token_refresh')
        refresh_data = {'refresh': refresh_token}
        response = self.client.post(refresh_url, refresh_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
