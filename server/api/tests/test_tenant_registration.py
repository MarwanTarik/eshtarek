from django.urls import reverse
from rest_framework import status
from api.tests.base import AuthAPITests
from api.enums.role import Role
from api.models import Users, Tenants, UserTenants


class TenantRegistrationTests(AuthAPITests):
    """Test cases for tenant registration"""
    
    def test_tenant_registration_success(self):
        """Test successful tenant registration"""
        url = reverse('tenant_registration')
        data = {
            'email': 'newtenant@example.com',
            'name': 'New Tenant Admin',
            'password': 'tenantpass123',
            'tenant_name': 'new_tenant'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)
        
        user = Users.objects.get(email='newtenant@example.com')
        self.assertEqual(user.name, 'New Tenant Admin')
        self.assertEqual(user.role, Role.TENANT_ADMIN)
        
        tenant = Tenants.objects.get(name='new_tenant')
        self.assertIsNotNone(tenant)
        
        self.assertTrue(UserTenants.objects.filter(user=user, tenant=tenant).exists())

    def test_tenant_registration_existing_tenant_name(self):
        """Test tenant registration with existing tenant name"""
        url = reverse('tenant_registration')
        data = {
            'email': 'newtenant@example.com',
            'name': 'New Tenant Admin',
            'password': 'tenantpass123',
            'tenant_name': 'test_tenant'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_tenant_registration_existing_email(self):
        """Test tenant registration with existing email"""
        url = reverse('tenant_registration')
        data = {
            'email': 'testuser@example.com',
            'name': 'New Tenant Admin',
            'password': 'tenantpass123',
            'tenant_name': 'new_tenant'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
