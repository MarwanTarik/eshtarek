from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from api.tests.base import AuthAPITests
from api.enums.limit_policies_metrics import LimitPoliciesMetrics
from api.enums.subscriptions_billing_cycle import SubscriptionsBillingCycle
from api.models import LimitPolicies, Plans, PlansLimitPolicies

class PlanLimitPolicyViewTests(AuthAPITests):
    """Test cases for PlanLimitPolicyView"""
    
    def setUp(self):
        super().setUp()
        
        # Create test limit policies
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
        
        # Create test plans
        self.test_plan1 = Plans.objects.create(
            name="Basic Plan",
            description="Basic plan for testing",
            billing_cycle=SubscriptionsBillingCycle.MONTHLY,
            billing_duration=1,
            price=29.99,
            created_by=self.test_admin
        )
        self.test_plan2 = Plans.objects.create(
            name="Premium Plan",
            description="Premium plan for testing",
            billing_cycle=SubscriptionsBillingCycle.ANNUALLY,
            billing_duration=1,
            price=299.99,
            created_by=self.test_admin
        )
        
        # Create test plan-limit policy association
        self.plan_limit_policy = PlansLimitPolicies.objects.create(
            plan=self.test_plan1,
            limit_policy=self.limit_policy1
        )

    def get_admin_auth_header(self):
        """Helper method to get admin authorization header"""
        refresh = RefreshToken.for_user(self.test_admin)
        return f'Bearer {str(refresh.access_token)}'

    def get_user_auth_header(self):
        """Helper method to get user authorization header"""
        refresh = RefreshToken.for_user(self.test_user)
        return f'Bearer {str(refresh.access_token)}'

    def test_create_plan_limit_policy_success(self):
        """Test successful plan-limit policy association creation"""
        url = reverse('plans_limit_policies_view')
        data = {
            'plan_id': str(self.test_plan2.id),
            'policy_id': str(self.limit_policy2.id)
        }
        
        self.client.credentials(HTTP_AUTHORIZATION=self.get_admin_auth_header())
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify association was created in database
        self.assertTrue(
            PlansLimitPolicies.objects.filter(
                plan=self.test_plan2,
                limit_policy=self.limit_policy2
            ).exists()
        )

    def test_create_plan_limit_policy_unauthorized(self):
        """Test plan-limit policy creation without admin permissions"""
        url = reverse('plans_limit_policies_view')
        data = {
            'plan_id': str(self.test_plan2.id),
            'policy_id': str(self.limit_policy2.id)
        }
        
        self.client.credentials(HTTP_AUTHORIZATION=self.get_user_auth_header())
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_plan_limit_policy_unauthenticated(self):
        """Test plan-limit policy creation without authentication"""
        url = reverse('plans_limit_policies_view')
        data = {
            'plan_id': str(self.test_plan2.id),
            'policy_id': str(self.limit_policy2.id)
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_plan_limit_policy_duplicate(self):
        """Test creating duplicate plan-limit policy association"""
        url = reverse('plans_limit_policies_view')
        data = {
            'plan_id': str(self.test_plan1.id),
            'policy_id': str(self.limit_policy1.id)
        }
        
        self.client.credentials(HTTP_AUTHORIZATION=self.get_admin_auth_header())
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_plan_limit_policy_nonexistent_plan(self):
        """Test creating association with nonexistent plan"""
        url = reverse('plans_limit_policies_view')
        data = {
            'plan_id': '00000000-0000-0000-0000-000000000000',
            'policy_id': str(self.limit_policy1.id)
        }
        
        self.client.credentials(HTTP_AUTHORIZATION=self.get_admin_auth_header())
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_plan_limit_policy_nonexistent_policy(self):
        """Test creating association with nonexistent policy"""
        url = reverse('plans_limit_policies_view')
        data = {
            'plan_id': str(self.test_plan1.id),
            'policy_id': '00000000-0000-0000-0000-000000000000'
        }
        
        self.client.credentials(HTTP_AUTHORIZATION=self.get_admin_auth_header())
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_plan_limit_policy_missing_fields(self):
        """Test creating association with missing fields"""
        url = reverse('plans_limit_policies_view')
        data = {
            'plan_id': str(self.test_plan1.id)
            # Missing policy_id
        }
        
        self.client.credentials(HTTP_AUTHORIZATION=self.get_admin_auth_header())
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_plan_limit_policy_success(self):
        """Test successful plan-limit policy association deletion"""
        url = reverse('plans_limit_policies_view')
        data = {
            'plan_id': str(self.test_plan1.id),
            'policy_id': str(self.limit_policy1.id)
        }
        
        self.client.credentials(HTTP_AUTHORIZATION=self.get_admin_auth_header())
        response = self.client.delete(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify association was deleted
        self.assertFalse(
            PlansLimitPolicies.objects.filter(
                plan=self.test_plan1,
                limit_policy=self.limit_policy1
            ).exists()
        )

    def test_delete_plan_limit_policy_not_found(self):
        """Test deleting nonexistent plan-limit policy association"""
        url = reverse('plans_limit_policies_view')
        data = {
            'plan_id': str(self.test_plan2.id),
            'policy_id': str(self.limit_policy2.id)
        }
        
        self.client.credentials(HTTP_AUTHORIZATION=self.get_admin_auth_header())
        response = self.client.delete(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_plan_limit_policy_unauthorized(self):
        """Test plan-limit policy deletion without admin permissions"""
        url = reverse('plans_limit_policies_view')
        data = {
            'plan_id': str(self.test_plan1.id),
            'policy_id': str(self.limit_policy1.id)
        }
        
        self.client.credentials(HTTP_AUTHORIZATION=self.get_user_auth_header())
        response = self.client.delete(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_plan_limit_policy_missing_fields(self):
        """Test deleting association with missing fields"""
        url = reverse('plans_limit_policies_view')
        data = {
            'plan_id': str(self.test_plan1.id)
            # Missing policy_id
        }
        
        self.client.credentials(HTTP_AUTHORIZATION=self.get_admin_auth_header())
        response = self.client.delete(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
