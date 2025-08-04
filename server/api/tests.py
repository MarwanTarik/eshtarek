from datetime import date, timedelta, datetime
from time import timezone
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password
from .models import Users, Tenants, UserTenants
from .enums.role import Role

class AuthAPITests(APITestCase):
    def setUp(self):
        """Set up test data and client"""        
        self.test_tenant = Tenants.objects.create(name="test_tenant")
        
        self.test_user = Users.objects.create(
            email="testuser@example.com",
            name="Test User",
            password=make_password("testpass123"),
            role=Role.TENANT_USER
        )
        
        self.test_admin = Users.objects.create(
            email="admin@example.com",
            name="Test Admin",
            password=make_password("adminpass123"),
            role=Role.PLATFORM_ADMIN
        )
        
        self.test_tenant_admin = Users.objects.create(
            email="tenantadmin@example.com",
            name="Tenant Admin",
            password=make_password("tenantpass123"),
            role=Role.TENANT_ADMIN
        )
        
        UserTenants.objects.create(user=self.test_user, tenant=self.test_tenant)
        UserTenants.objects.create(user=self.test_tenant_admin, tenant=self.test_tenant)

    def tearDown(self):
        """Clean up after tests"""
        Users.objects.all().delete()
        Tenants.objects.all().delete()
        UserTenants.objects.all().delete()


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

