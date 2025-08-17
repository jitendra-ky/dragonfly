from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserViewTestCase(APITestCase):
    """Minimal test cases for UserView"""
    
    def setUp(self):
        """Set up test data"""
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
        self.existing_user = User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='existingpass123'
        )
        
    def test_post_create_user_success(self):
        """Test successful user creation via POST"""
        response = self.client.post('/api/auth/users/', self.user_data, format='json')
        
        # Check response status and basic structure
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['username'], self.user_data['username'])
        self.assertEqual(response.data['email'], self.user_data['email'])
        
        # Verify user was created in database
        created_user = User.objects.get(username=self.user_data['username'])
        self.assertIsNotNone(created_user)
        self.assertEqual(created_user.email, self.user_data['email'])


class JWTAuthTestCase(APITestCase):
    """Minimal test cases for JWT authentication"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.login_data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }

    def test_create_user(self):
        """Test user creation"""
        user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword123'
        }
        response = self.client.post('/api/auth/users/', user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_token_obtain(self):
        """Test JWT token generation"""
        response = self.client.post('/api/auth/token/', self.login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_token_refresh(self):
        """Test JWT token refresh"""
        # Get tokens
        response = self.client.post('/api/auth/token/', self.login_data, format='json')
        refresh_token = response.data['refresh']
        
        # Refresh token
        refresh_data = {'refresh': refresh_token}
        response = self.client.post('/api/auth/token/refresh/', refresh_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_authenticated_access(self):
        """Test accessing protected endpoint with JWT"""
        # Create token
        refresh = RefreshToken.for_user(self.user)
        access_token = refresh.access_token
        
        # Access protected endpoint
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get('/api/auth/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)

    def test_unauthenticated_access(self):
        """Test accessing protected endpoint without authentication"""
        response = self.client.get('/api/auth/users/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
