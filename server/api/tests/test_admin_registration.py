from django.urls import reverse
from rest_framework import status
from api.tests.base import AuthAPITests
from api.enums.role import Role
from api.models import Users


class AdminRegistrationTests(AuthAPITests):
    """Test cases for admin registration"""
    
    def test_admin_registration_success(self):
        """Test successful admin registration"""
        url = reverse('admin_registration')
        data = {
            'email': 'newadmin@example.com',
            'name': 'New Admin',
            'password': 'adminpass123'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)
        
        user = Users.objects.get(email='newadmin@example.com')
        self.assertEqual(user.name, 'New Admin')
        self.assertEqual(user.role, Role.PLATFORM_ADMIN)

    def test_admin_registration_existing_email(self):
        """Test admin registration with existing email"""
        url = reverse('admin_registration')
        data = {
            'email': 'admin@example.com',
            'name': 'Another Admin',
            'password': 'adminpass123'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_admin_registration_missing_fields(self):
        """Test admin registration with missing required fields"""
        url = reverse('admin_registration')
        data = {
            'email': 'newadmin@example.com',
            'name': 'New Admin'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
