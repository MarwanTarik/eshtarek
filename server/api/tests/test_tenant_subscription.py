from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from api.tests.base import AuthAPITests
from api.enums.limit_policies_metrics import LimitPoliciesMetrics
from api.enums.subscriptions_billing_cycle import SubscriptionsBillingCycle
from api.enums.subscriptions_status import SubscriptionsStatus
from api.models import LimitPolicies, Plans, PlansLimitPolicies, Subscriptions
from datetime import datetime, timezone


class SubscriptionViewTests(AuthAPITests):
    """Test cases for SubscriptionView"""
    
    def setUp(self):
        super().setUp()
        
        self.limit_policy = LimitPolicies.objects.create(
            metric=LimitPoliciesMetrics.MAX_USERS.value,
            limit=10,
            created_by=self.test_admin
        )
        
        self.test_plan = Plans.objects.create(
            name="Basic Plan",
            description="Basic plan for testing",
            billing_cycle=SubscriptionsBillingCycle.MONTHLY.value,
            billing_duration=1,
            price=29.99,
            created_by=self.test_admin
        )
        
        self.premium_plan = Plans.objects.create(
            name="Premium Plan",
            description="Premium plan for testing",
            billing_cycle=SubscriptionsBillingCycle.ANNUALLY.value,
            billing_duration=1,
            price=299.99,
            created_by=self.test_admin
        )
        
        PlansLimitPolicies.objects.create(plan=self.test_plan, limit_policy=self.limit_policy)
        
        self.test_subscription = Subscriptions.objects.create(
            plan=self.test_plan,
            tenant=self.test_tenant,
            created_by_user=self.test_tenant_admin,
            status=SubscriptionsStatus.ACTIVE
        )

    def get_admin_auth_header(self):
        """Helper method to get admin authorization header"""
        refresh = RefreshToken.for_user(self.test_admin)
        return f'Bearer {str(refresh.access_token)}'

    def get_tenant_admin_auth_header(self):
        """Helper method to get tenant admin authorization header"""
        refresh = RefreshToken.for_user(self.test_tenant_admin)
        return f'Bearer {str(refresh.access_token)}'

    def get_user_auth_header(self):
        """Helper method to get user authorization header"""
        refresh = RefreshToken.for_user(self.test_user)
        return f'Bearer {str(refresh.access_token)}'

    def test_create_subscription_as_admin_forbidden(self):
        """Creating a subscription as admin should be forbidden"""
        url = reverse('subscription_view')
        data = {
            'plan_id': str(self.premium_plan.id)
        }
        
        response = self.client.post(
            url,
            data,
            HTTP_AUTHORIZATION=self.get_admin_auth_header(),
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_subscription_as_tenant_admin_success(self):
        """Creating a subscription as tenant admin should be successful"""
        url = reverse('subscription_view')
        data = {
            'plan_id': str(self.premium_plan.id)
        }
        
        response = self.client.post(
            url,
            data,
            HTTP_AUTHORIZATION=self.get_tenant_admin_auth_header(),
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_subscription_as_user_forbidden(self):
        """Creating a subscription as regular user should be forbidden"""
        url = reverse('subscription_view')
        data = {
            'plan_id': str(self.test_plan.id)
        }
        
        response = self.client.post(
            url,
            data,
            HTTP_AUTHORIZATION=self.get_user_auth_header(),
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_subscription_without_auth_unauthorized(self):
        """Creating a subscription without authentication should be unauthorized"""
        url = reverse('subscription_view')
        data = {
            'plan_id': str(self.test_plan.id)
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_subscription_invalid_plan_id(self):
        """Creating a subscription with invalid plan_id should be forbidden"""
        url = reverse('subscription_view')
        data = {
            'plan_id': 'invalid_uuid'
        }
        
        response = self.client.post(
            url,
            data,
            HTTP_AUTHORIZATION=self.get_tenant_admin_auth_header(),
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_subscription_missing_plan_id(self):
        """Creating a subscription without plan_id"""
        url = reverse('subscription_view')
        data = {}
        
        response = self.client.post(
            url,
            data,
            HTTP_AUTHORIZATION=self.get_tenant_admin_auth_header(),
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_all_subscriptions_as_admin_success(self):
        """Getting all subscriptions as admin"""
        url = reverse('subscription_view')
        
        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=self.get_admin_auth_header()
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreater(len(response.data), 0)
        
        # Check that our test subscription is in the response
        subscription_ids = [sub['id'] for sub in response.data]
        self.assertIn(str(self.test_subscription.id), subscription_ids)

    def test_get_specific_subscription_success(self):
        """Getting a specific subscription by ID"""
        url = reverse('subscription_detail', kwargs={'pk': self.test_subscription.id})
        
        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=self.get_tenant_admin_auth_header()
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.test_subscription.id))
        self.assertEqual(response.data['plan']['id'], str(self.test_plan.id))

    def test_update_subscription_success(self):
        """Updating a subscription successfully"""
        url = reverse('subscription_detail', kwargs={'pk': self.test_subscription.id})
        data = {
            'plan_id': str(self.premium_plan.id)
        }
        
        response = self.client.put(
            url,
            data,
            HTTP_AUTHORIZATION=self.get_tenant_admin_auth_header(),
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['plan']['id'], str(self.premium_plan.id))
        
        # Verify plan was updated in database
        updated_subscription = Subscriptions.objects.get(id=self.test_subscription.id)
        self.assertEqual(updated_subscription.plan, self.premium_plan)

    def test_delete_subscription_success(self):
        """Deleting (cancelling) a subscription successfully"""
        url = reverse('subscription_detail', kwargs={'pk': self.test_subscription.id})
        
        response = self.client.delete(
            url,
            HTTP_AUTHORIZATION=self.get_admin_auth_header()
        )
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data['message'], 'Subscription deleted successfully')
        
        # Verify subscription status was changed to CANCELLED (not actually deleted)
        updated_subscription = Subscriptions.objects.get(id=self.test_subscription.id)
        self.assertEqual(updated_subscription.status, SubscriptionsStatus.CANCELLED)

    def tearDown(self):
        """Clean up after tests"""
        super().tearDown()
        Subscriptions.objects.all().delete()
        Plans.objects.all().delete()
        LimitPolicies.objects.all().delete()
        PlansLimitPolicies.objects.all().delete()
