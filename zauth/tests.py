from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from zauth.views import UserView

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
