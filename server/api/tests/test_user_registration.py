from django.urls import reverse
from rest_framework import status
from api.tests.base import AuthAPITests
from api.enums.role import Role
from api.models import Users, UserTenants


class UserRegistrationTests(AuthAPITests):
    """Test cases for user registration"""
    
    def test_user_registration_success(self):
        """Test successful user registration"""
        url = reverse('user_registration')
        data = {
            'email': 'newuser@example.com',
            'name': 'New User',
            'password': 'newpass123',
            'tenant_name': 'test_tenant'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)
        
        user = Users.objects.get(email='newuser@example.com')
        self.assertEqual(user.name, 'New User')
        self.assertEqual(user.role, Role.TENANT_USER)
        
        self.assertTrue(UserTenants.objects.filter(user=user, tenant=self.test_tenant).exists())

    def test_user_registration_existing_email(self):
        """Test user registration with existing email"""
        url = reverse('user_registration')
        data = {
            'email': 'testuser@example.com',
            'name': 'Another User',
            'password': 'newpass123',
            'tenant_name': 'test_tenant'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_user_registration_nonexistent_tenant(self):
        """Test user registration with nonexistent tenant"""
        url = reverse('user_registration')
        data = {
            'email': 'newuser@example.com',
            'name': 'New User',
            'password': 'newpass123',
            'tenant_name': 'nonexistent_tenant'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_missing_fields(self):
        """Test user registration with missing required fields"""
        url = reverse('user_registration')
        data = {
            'email': 'newuser@example.com',
            'name': 'New User'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
        self.assertIn('tenant_name', response.data)

    def test_user_registration_invalid_email(self):
        """Test user registration with invalid email format"""
        url = reverse('user_registration')
        data = {
            'email': 'invalid-email',
            'name': 'New User',
            'password': 'newpass123',
            'tenant_name': 'test_tenant'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
