import uuid
import django.db.models as models

from server.api.enums.subscriptions_billing_cycle import SubscriptionsBillingCycle
from .enums.role import Role
from .enums.limit_policies_metrics import LimitPoliciesMetrics
from .enums.subscriptions_status import SubscriptionsStatus

class Users(models.Model):
    id = models.UUIDField(auto_created=True, primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=500, required=True)
    role = models.CharField(max_length=50, choices=Role.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        constraints = [
            models.UniqueConstraint(fields=['email'], name='unique_email_constraint')
        ]
        indexes = [
            models.Index(fields=['email'], name='email_index'),
            models.Index(fields=['role'], name='role_index')
        ]
        
    def __str__(self):
        return 'name: {}, email: {} - role: {}'.format(self.name, self.email, self.role)


class Tenants(models.Model):
    id = models.UUIDField(auto_created=True, primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tenants'
        verbose_name = 'Tenant'
        verbose_name_plural = 'Tenants'
        constraints = [
            models.UniqueConstraint(fields=['name'], name='unique_tenant_name_constraint')
        ]
    
    def __str__(self):
        return 'Tenant: {}'.format(self.name)
    

class UserTenants(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='user_tenants')
    tenant = models.ForeignKey(Tenants, on_delete=models.CASCADE, related_name='tenant_users')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_tenants'
        verbose_name = 'User Tenant'
        verbose_name_plural = 'User Tenants'
        unique_together = (('user', 'tenant'),)
    
    def __str__(self):
        return 'User: {}, Tenant: {}'.format(self.user.name, self.tenant.name)
    
class Plans(models.Model):
    id = models.UUIDField(auto_created=True, primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    billing_cycle = models.CharField(max_length=20, choices=SubscriptionsBillingCycle.choices)
    billing_duration = models.PositiveIntegerField(help_text='Duration in months for monthly plans or years for yearly plans')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='created_plans')

    class Meta:
        db_table = 'plans'
        verbose_name = 'Plan'
        verbose_name_plural = 'Plans'
        constraints = [
            models.UniqueConstraint(fields=['name'], name='unique_plan_name_constraint')
        ]
    
    def __str__(self):
        return 'Plan: {}, Price: {}'.format(self.name, self.price)

class LimitPolicies(models.Model):
    id = models.UUIDField(auto_created=True, primary_key=True, default=uuid.uuid4, editable=False)
    metric = models.CharField(max_length=50, choices=LimitPoliciesMetrics.choices)
    limit = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='created_limit_policies')

    class Meta:
        db_table = 'limit_policies'
        verbose_name = 'Limit Policy'
        verbose_name_plural = 'Limit Policies'
        constraints = [
            models.UniqueConstraint(fields=['metric'], name='unique_limit_policy_metric_constraint')
        ]
        indexes = [
            models.Index(fields=['metric'], name='metric_index')
        ]

    def __str__(self):
        return 'Metric: {}, Limit: {}'.format(self.metric, self.limit)
    

class PlansLimitPolicies(models.Model):
    plan = models.ForeignKey(Plans, on_delete=models.CASCADE, related_name='plan_limit_policies')
    limit_policy = models.ForeignKey(LimitPolicies, on_delete=models.CASCADE, related_name='limit_policy_plans')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'plans_limit_policies'
        verbose_name = 'Plan Limit Policy'
        verbose_name_plural = 'Plan Limit Policies'
        unique_together = (('plan', 'limit_policy'),)
    
    def __str__(self):
        return 'Plan: {}, Limit Policy: {}'.format(self.plan.name, self.limit_policy.metric)
    

class Subscriptions(models.Model):
    id = models.UUIDField(auto_created=True, primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(max_length=50, choices=SubscriptionsStatus.choices)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by_user_id = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='created_subscriptions')
    plan_id = models.ForeignKey(Plans, on_delete=models.CASCADE, related_name='plan_subscriptions')
    tenant_id = models.ForeignKey(Tenants, on_delete=models.CASCADE, related_name='tenant_subscriptions')

    class Meta:
        db_table = 'subscriptions'
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
        constraints = [
            models.UniqueConstraint(fields=['created_by_user_id', 'plan_id', 'tenant_id'], name='unique_subscription_constraint')
        ]
        indexes = [
            models.Index(fields=['status'], name='status_index'),
            models.Index(fields=['created_by_user_id'], name='created_by_user_index'),
            models.Index(fields=['plan_id'], name='plan_index'),
            models.Index(fields=['tenant_id'], name='tenant_index')
        ]
    
    def __str__(self):
        return 'Subscription: {}, Status: {}, Plan: {}, Tenant: {}'.format(
            self.id, self.status, self.plan_id.name, self.tenant_id.name
        )
    
class Usages(models.Model):
    id = models.UUIDField(auto_created=True, primary_key=True, default=uuid.uuid4, editable=False)
    metric = models.CharField(max_length=50, choices=LimitPoliciesMetrics.choices)
    value = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    subscription_id = models.ForeignKey(Subscriptions, on_delete=models.CASCADE, related_name='subscription_usages')

    class Meta:
        db_table = 'usages'
        verbose_name = 'Usage'
        verbose_name_plural = 'Usages'
        constraints = [
            models.UniqueConstraint(fields=['subscription_id', 'metric'], name='unique_usage_constraint')
        ]
        indexes = [
            models.Index(fields=['metric'], name='usage_metric_index'),
            models.Index(fields=['subscription_id'], name='usage_subscription_index')
        ]
    
    def __str__(self):
        return 'Usage: {}, Metric: {}, Value: {}'.format(self.id, self.metric, self.value)
    