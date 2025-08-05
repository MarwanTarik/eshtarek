from datetime import date, timedelta, datetime
from time import timezone
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password
from api.models import Users, Tenants, UserTenants, Plans, LimitPolicies, PlansLimitPolicies
from api.enums.role import Role
from api.enums.limit_policies_metrics import LimitPoliciesMetrics
from api.enums.subscriptions_billing_cycle import SubscriptionsBillingCycle



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
