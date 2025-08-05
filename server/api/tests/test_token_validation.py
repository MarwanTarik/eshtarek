from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from api.tests.base import AuthAPITests
from api.enums.role import Role


class TokenValidationTests(AuthAPITests):
    """Test cases for token validation and JWT features"""
    
    def test_token_contains_user_info(self):
        """Test that tokens contain user information"""
        url = reverse('login')
        data = {
            'email': 'testuser@example.com',
            'password': 'testpass123'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        access_token = response.data['access']
        refresh_token = RefreshToken(response.data['refresh'])
        
        self.assertEqual(refresh_token['role'], self.test_user.role)
        self.assertEqual(refresh_token['id'], str(self.test_user.id))

    def test_different_user_roles_login(self):
        """Test login for different user roles"""
        test_cases = [
            ('testuser@example.com', 'testpass123', Role.TENANT_USER),
            ('admin@example.com', 'adminpass123', Role.PLATFORM_ADMIN),
            ('tenantadmin@example.com', 'tenantpass123', Role.TENANT_ADMIN),
        ]
        
        for email, password, expected_role in test_cases:
            with self.subTest(email=email, role=expected_role):
                url = reverse('login')
                data = {
                    'email': email,
                    'password': password
                }
                
                response = self.client.post(url, data, format='json')
                
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                
                refresh_token = RefreshToken(response.data['refresh'])
                self.assertEqual(refresh_token['role'], expected_role)
