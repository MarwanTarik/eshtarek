from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from api.tests.base import AuthAPITests
from api.enums.limit_policies_metrics import LimitPoliciesMetrics
from api.enums.subscriptions_billing_cycle import SubscriptionsBillingCycle
from api.models import LimitPolicies, Plans, PlansLimitPolicies


class PlanViewTests(AuthAPITests):
    """Test cases for PlanView"""
    
    def setUp(self):
        super().setUp()
        
        # Create limit policies for testing
        self.limit_policy1 = LimitPolicies.objects.create(
            metric=LimitPoliciesMetrics.MAX_USERS,
            limit=10,
            created_by=self.test_admin
        )
        self.limit_policy2 = LimitPolicies.objects.create(
            metric=LimitPoliciesMetrics.MAX_USERS,
            limit=50,
            created_by=self.test_admin
        )
        
        # Create a test plan
        self.test_plan = Plans.objects.create(
            name="Basic Plan",
            description="Basic plan for testing",
            billing_cycle=SubscriptionsBillingCycle.MONTHLY,
            billing_duration=1,
            price=29.99,
            created_by=self.test_admin
        )
        
        # Associate limit policies with the plan
        PlansLimitPolicies.objects.create(plan=self.test_plan, limit_policy=self.limit_policy1)

    def get_admin_auth_header(self):
        """Helper method to get admin authorization header"""
        refresh = RefreshToken.for_user(self.test_admin)
        return f'Bearer {str(refresh.access_token)}'

    def get_user_auth_header(self):
        """Helper method to get user authorization header"""
        refresh = RefreshToken.for_user(self.test_user)
        return f'Bearer {str(refresh.access_token)}'

    def test_create_plan_success(self):
        """Test successful plan creation by admin"""
        url = reverse('plans_view')
        data = {
            'name': 'Premium Plan',
            'description': 'Premium plan with advanced features',
            'billing_cycle': SubscriptionsBillingCycle.ANNUALLY.value,
            'billing_duration': 1,
            'price': 299.99,
            'policy_ids': [str(self.limit_policy1.id), str(self.limit_policy2.id)],
        }
        self.client.credentials(HTTP_AUTHORIZATION=self.get_admin_auth_header())
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Premium Plan')
        self.assertEqual(response.data['price'], '299.99')
        
        # Verify plan was created in database
        plan = Plans.objects.get(name='Premium Plan')
        self.assertEqual(plan.description, 'Premium plan with advanced features')
        self.assertEqual(plan.created_by, self.test_admin)
        
        # Verify plan limit policies were created
        self.assertEqual(plan.plan_limit_policies.count(), 2)

    def test_create_plan_unauthorized(self):
        """Test plan creation without admin permissions"""
        url = reverse('plans_view')
        data = {
            'name': 'Unauthorized Plan',
            'billing_cycle': SubscriptionsBillingCycle.MONTHLY,
            'billing_duration': 1,
            'price': 19.99,
            'policy_ids': [str(self.limit_policy1.id)]
        }
        
        self.client.credentials(HTTP_AUTHORIZATION=self.get_user_auth_header())
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_plan_unauthenticated(self):
        """Test plan creation without authentication"""
        url = reverse('plans_view')
        data = {
            'name': 'Unauthenticated Plan',
            'billing_cycle': SubscriptionsBillingCycle.MONTHLY,
            'billing_duration': 1,
            'price': 19.99,
            'policy_ids': [str(self.limit_policy1.id)]
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_plan_invalid_data(self):
        """Test plan creation with invalid data"""
        url = reverse('plans_view')
        data = {
            'name': '',  # Empty name
            'billing_cycle': 'invalid_cycle',
            'billing_duration': -1,  # Negative duration
            'price': -10.00,  # Negative price
            'policy_ids': []
        }
        
        self.client.credentials(HTTP_AUTHORIZATION=self.get_admin_auth_header())
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_plan_nonexistent_policy(self):
        """Test plan creation with nonexistent policy ID"""
        url = reverse('plans_view')
        data = {
            'name': 'Plan with Invalid Policy',
            'billing_cycle': SubscriptionsBillingCycle.MONTHLY,
            'billing_duration': 1,
            'price': 29.99,
            'policy_ids': ['00000000-0000-0000-0000-000000000000']  # Non-existent UUID
        }
        
        self.client.credentials(HTTP_AUTHORIZATION=self.get_admin_auth_header())
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_plan_duplicate_name(self):
        """Test plan creation with duplicate name"""
        url = reverse('plans_view')
        data = {
            'name': 'Basic Plan',  # Same as existing plan
            'billing_cycle': SubscriptionsBillingCycle.MONTHLY,
            'billing_duration': 1,
            'price': 29.99,
            'policy_ids': [str(self.limit_policy1.id)]
        }
        
        self.client.credentials(HTTP_AUTHORIZATION=self.get_admin_auth_header())
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_all_plans_success(self):
        """Test retrieving all plans"""
        url = reverse('plans_view')
        
        self.client.credentials(HTTP_AUTHORIZATION=self.get_admin_auth_header())
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Basic Plan')

    def test_get_all_plans_unauthorized(self):
        """Test retrieving all plans without admin permissions"""
        url = reverse('plans_view')
        
        self.client.credentials(HTTP_AUTHORIZATION=self.get_user_auth_header())
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_plan_by_id_success(self):
        """Test retrieving specific plan by ID"""
        url = reverse('plan_detail', kwargs={'pk': self.test_plan.id})
        
        self.client.credentials(HTTP_AUTHORIZATION=self.get_admin_auth_header())
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Basic Plan')
        self.assertEqual(response.data['id'], str(self.test_plan.id))

    def test_get_plan_by_id_not_found(self):
        """Test retrieving nonexistent plan"""
        url = reverse('plan_detail', kwargs={'pk': '00000000-0000-0000-0000-000000000000'})
        
        self.client.credentials(HTTP_AUTHORIZATION=self.get_admin_auth_header())
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_plan_success(self):
        """Test successful plan update"""
        url = reverse('plan_detail', kwargs={'pk': self.test_plan.id})
        data = {
            'name': 'Updated Basic Plan',
            'description': 'Updated description',
            'price': 39.99
        }
        
        self.client.credentials(HTTP_AUTHORIZATION=self.get_admin_auth_header())
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Basic Plan')
        self.assertEqual(response.data['price'], '39.99')
        
        # Verify update in database
        updated_plan = Plans.objects.get(id=self.test_plan.id)
        self.assertEqual(updated_plan.name, 'Updated Basic Plan')

    def test_update_plan_not_found(self):
        """Test updating nonexistent plan"""
        url = reverse('plan_detail', kwargs={'pk': '00000000-0000-0000-0000-000000000000'})
        data = {'name': 'Updated Plan'}
        
        self.client.credentials(HTTP_AUTHORIZATION=self.get_admin_auth_header())
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_plan_unauthorized(self):
        """Test plan update without admin permissions"""
        url = reverse('plan_detail', kwargs={'pk': self.test_plan.id})
        data = {'name': 'Unauthorized Update'}
        
        self.client.credentials(HTTP_AUTHORIZATION=self.get_user_auth_header())
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_plan_success(self):
        """Test successful plan deletion"""
        url = reverse('plan_detail', kwargs={'pk': self.test_plan.id})
        
        self.client.credentials(HTTP_AUTHORIZATION=self.get_admin_auth_header())
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify plan was deleted
        self.assertFalse(Plans.objects.filter(id=self.test_plan.id).exists())

    def test_delete_plan_not_found(self):
        """Test deleting nonexistent plan"""
        url = reverse('plan_detail', kwargs={'pk': '00000000-0000-0000-0000-000000000000'})
        
        self.client.credentials(HTTP_AUTHORIZATION=self.get_admin_auth_header())
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_plan_unauthorized(self):
        """Test plan deletion without admin permissions"""
        url = reverse('plan_detail', kwargs={'pk': self.test_plan.id})
        
        self.client.credentials(HTTP_AUTHORIZATION=self.get_user_auth_header())
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
