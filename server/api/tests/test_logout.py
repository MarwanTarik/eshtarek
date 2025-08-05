from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from api.tests.base import AuthAPITests


class LogoutTests(AuthAPITests):
    """Test cases for user logout"""
    
    def test_logout_success(self):
        """Test successful logout"""
        refresh = RefreshToken.for_user(self.test_user)
        access_token = str(refresh.access_token)
        
        url = reverse('logout')
        data = {
            'refresh': str(refresh)
        }
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Successfully logged out', response.data['message'])

    def test_logout_missing_refresh_token(self):
        """Test logout without refresh token"""
        refresh = RefreshToken.for_user(self.test_user)
        access_token = str(refresh.access_token)
        
        url = reverse('logout')
        data = {} 
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_invalid_refresh_token(self):
        """Test logout with invalid refresh token"""
        refresh = RefreshToken.for_user(self.test_user)
        access_token = str(refresh.access_token)
        
        url = reverse('logout')
        data = {
            'refresh': 'invalid_refresh_token'
        }
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Invalid token', response.data['error'])

    def test_logout_unauthenticated(self):
        """Test logout without authentication"""
        url = reverse('logout')
        data = {
            'refresh': 'some_refresh_token'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
