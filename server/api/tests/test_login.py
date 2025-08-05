from django.urls import reverse
from rest_framework import status
from api.tests.base import AuthAPITests


class LoginTests(AuthAPITests):
    """Test cases for user login"""
    
    def test_login_success(self):
        """Test successful login"""
        url = reverse('login')
        data = {
            'email': 'testuser@example.com',
            'password': 'testpass123'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)

    def test_login_invalid_email(self):
        """Test login with invalid email"""
        url = reverse('login')
        data = {
            'email': 'nonexistent@example.com',
            'password': 'testpass123'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Invalid email or password', str(response.data))

    def test_login_invalid_password(self):
        """Test login with invalid password"""
        url = reverse('login')
        data = {
            'email': 'testuser@example.com',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Invalid email or password', str(response.data))

    def test_login_missing_fields(self):
        """Test login with missing required fields"""
        url = reverse('login')
        data = {
            'email': 'testuser@example.com'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_empty_credentials(self):
        """Test login with empty credentials"""
        url = reverse('login')
        data = {}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_invalid_email_format(self):
        """Test login with invalid email format"""
        url = reverse('login')
        data = {
            'email': 'invalid-email',
            'password': 'testpass123'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
