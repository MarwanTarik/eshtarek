from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from api.tests.base import AuthAPITests
from api.enums.limit_policies_metrics import LimitPoliciesMetrics
from api.models import LimitPolicies


class LimitPoliciesViewTests(AuthAPITests):
    """Test cases for LimitPoliciesView"""
    
    def setUp(self):
        super().setUp()
        
        # Create a test limit policy
        self.test_limit_policy = LimitPolicies.objects.create(
            metric=LimitPoliciesMetrics.MAX_USERS,
            limit=25,
            created_by=self.test_admin
        )

    def get_admin_auth_header(self):
        """Helper method to get admin authorization header"""
        refresh = RefreshToken.for_user(self.test_admin)
        return f'Bearer {str(refresh.access_token)}'

    def get_user_auth_header(self):
        """Helper method to get user authorization header"""
        refresh = RefreshToken.for_user(self.test_user)
        return f'Bearer {str(refresh.access_token)}'

    def test_create_limit_policy_success(self):
        """Test successful limit policy creation by admin"""
        url = reverse('limit_policies_view')
        data = {
            'metric': LimitPoliciesMetrics.MAX_USERS.value,
            'limit': 100,
            'created_by': self.test_admin.id 
        }
        
        self.client.credentials(HTTP_AUTHORIZATION=self.get_admin_auth_header())
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['metric'], LimitPoliciesMetrics.MAX_USERS.value)
        self.assertEqual(response.data['limit'], 100)
        
        # Verify limit policy was created in database
        limit_policy = LimitPolicies.objects.get(limit=100)
        self.assertEqual(limit_policy.created_by, self.test_admin)

    def test_create_limit_policy_unauthorized(self):
        """Test limit policy creation without admin permissions"""
        url = reverse('limit_policies_view')
        data = {
            'metric': LimitPoliciesMetrics.MAX_USERS.value,
            'limit': 50
        }
        
        self.client.credentials(HTTP_AUTHORIZATION=self.get_user_auth_header())
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_limit_policy_unauthenticated(self):
        """Test limit policy creation without authentication"""
        url = reverse('limit_policies_view')
        data = {
            'metric': LimitPoliciesMetrics.MAX_USERS.value,
            'limit': 50
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_limit_policy_invalid_data(self):
        """Test limit policy creation with invalid data"""
        url = reverse('limit_policies_view')
        data = {
            'metric': 'invalid_metric',
            'limit': -5  # Negative limit
        }
        
        self.client.credentials(HTTP_AUTHORIZATION=self.get_admin_auth_header())
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_limit_policy_missing_fields(self):
        """Test limit policy creation with missing required fields"""
        url = reverse('limit_policies_view')
        data = {
            'metric': LimitPoliciesMetrics.MAX_USERS.value
            # Missing 'limit' field
        }
        
        self.client.credentials(HTTP_AUTHORIZATION=self.get_admin_auth_header())
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_all_limit_policies_success(self):
        """Test retrieving all limit policies"""
        url = reverse('limit_policies_view')
        
        self.client.credentials(HTTP_AUTHORIZATION=self.get_admin_auth_header())
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['limit'], 25)

    def test_get_all_limit_policies_unauthorized(self):
        """Test retrieving all limit policies without admin permissions"""
        url = reverse('limit_policies_view')
        
        self.client.credentials(HTTP_AUTHORIZATION=self.get_user_auth_header())
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_limit_policy_by_id_success(self):
        """Test retrieving specific limit policy by ID"""
        url = reverse('limit_policy_detail', kwargs={'pk': self.test_limit_policy.id})
        
        self.client.credentials(HTTP_AUTHORIZATION=self.get_admin_auth_header())
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['limit'], 25)
        self.assertEqual(response.data['id'], str(self.test_limit_policy.id))

    def test_get_limit_policy_by_id_not_found(self):
        """Test retrieving nonexistent limit policy"""
        url = reverse('limit_policy_detail', kwargs={'pk': '00000000-0000-0000-0000-000000000000'})
        
        self.client.credentials(HTTP_AUTHORIZATION=self.get_admin_auth_header())
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_limit_policy_success(self):
        """Test successful limit policy update"""
        url = reverse('limit_policy_detail', kwargs={'pk': self.test_limit_policy.id})
        data = {
            'limit': 75
        }
        
        self.client.credentials(HTTP_AUTHORIZATION=self.get_admin_auth_header())
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['limit'], 75)
        
        # Verify update in database
        updated_policy = LimitPolicies.objects.get(id=self.test_limit_policy.id)
        self.assertEqual(updated_policy.limit, 75)

    def test_update_limit_policy_not_found(self):
        """Test updating nonexistent limit policy"""
        url = reverse('limit_policy_detail', kwargs={'pk': '00000000-0000-0000-0000-000000000000'})
        data = {'limit': 100}
        
        self.client.credentials(HTTP_AUTHORIZATION=self.get_admin_auth_header())
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_limit_policy_unauthorized(self):
        """Test limit policy update without admin permissions"""
        url = reverse('limit_policy_detail', kwargs={'pk': self.test_limit_policy.id})
        data = {'limit': 100}
        
        self.client.credentials(HTTP_AUTHORIZATION=self.get_user_auth_header())
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_limit_policy_success(self):
        """Test successful limit policy deletion"""
        url = reverse('limit_policy_detail', kwargs={'pk': self.test_limit_policy.id})
        
        self.client.credentials(HTTP_AUTHORIZATION=self.get_admin_auth_header())
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        self.assertFalse(LimitPolicies.objects.filter(id=self.test_limit_policy.id).exists())

    def test_delete_limit_policy_not_found(self):
        """Test deleting nonexistent limit policy"""
        url = reverse('limit_policy_detail', kwargs={'pk': '00000000-0000-0000-0000-000000000000'})
        
        self.client.credentials(HTTP_AUTHORIZATION=self.get_admin_auth_header())
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_limit_policy_unauthorized(self):
        """Test limit policy deletion without admin permissions"""
        url = reverse('limit_policy_detail', kwargs={'pk': self.test_limit_policy.id})
        
        self.client.credentials(HTTP_AUTHORIZATION=self.get_user_auth_header())
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
