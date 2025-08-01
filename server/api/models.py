from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, EmailValidator
from django.core.exceptions import ValidationError
from .enums.role import Role
from .enums.subscriptions_status import SubscriptionsStatus
import uuid
from decimal import Decimal

# Create your models here.
class Tenants(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tenants'
        verbose_name = 'Tenant'
        verbose_name_plural = 'Tenants'

    def validate(self):
        if self.name:
            self.name = self.name.strip()
        if not self.name:
            raise ValidationError('Tenant name cannot be empty or just whitespace.')

    def save(self, *args, **kwargs):
        self.validate()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Tenant: {self.name} (ID: {self.id})"


class Users(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, validators=[MinValueValidator(1)])
    role = models.CharField(max_length=50, choices=Role.choices, default=Role.GUEST)
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    password = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['email'], name='users_email_idx'),
            models.Index(fields=['role'], name='users_role_idx'),
        ]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f"User: {self.name} ({self.email})"
    
class UserTenants(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='user_tenants')
    tenant = models.ForeignKey(Tenants, on_delete=models.CASCADE, related_name='tenant_users')

    class Meta:
        db_table = 'user_tenants'
        verbose_name = 'User Tenant'
        verbose_name_plural = 'User Tenants'
        unique_together = (('user', 'tenant'),)
        indexes = [
            models.Index(fields=['user'], name='user_tenants_user_idx'),
            models.Index(fields=['tenant'], name='user_tenants_tenant_idx'),
        ]

    def __str__(self):
        return f"User: {self.user.name} -> Tenant: {self.tenant.name}"

class Plans(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    billing_duration = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(365)])  # days
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tenant_id = models.ForeignKey(Tenants, on_delete=models.CASCADE, related_name='plans')
    created_by = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='created_plans')

    class Meta:
        db_table = 'plans'
        verbose_name = 'Plan'
        verbose_name_plural = 'Plans'
        unique_together = (('name', 'tenant_id'),)
        indexes = [
            models.Index(fields=['name'], name='plans_name_idx'),
            models.Index(fields=['tenant_id'], name='plans_tenant_idx'),
            models.Index(fields=['price'], name='plans_price_idx'),
        ]

    def validate(self):
        if not self.name:
            raise ValidationError('Plan name cannot be empty or just whitespace.')
        if self.price < 0:
            raise ValidationError('Price cannot be negative.')
        if self.billing_duration <= 0:
            raise ValidationError('Billing duration must be at least 1 day.')

    def save(self, *args, **kwargs):
        self.validate()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Plan: {self.name} (${self.price}/{self.billing_duration} days)"

class LimitPolicies(models.Model): 
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    metric = models.CharField(max_length=255)
    limit = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tenant_id = models.ForeignKey(Tenants, on_delete=models.CASCADE, related_name='limit_policies')
    created_by = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='created_limit_policies')

    class Meta:
        db_table = 'limit_policies'
        verbose_name = 'Limit Policy'
        verbose_name_plural = 'Limit Policies'
        unique_together = (('metric', 'tenant_id'),)
        indexes = [
            models.Index(fields=['metric'], name='limit_policies_metric_idx'),
            models.Index(fields=['tenant_id'], name='limit_policies_tenant_idx'),
        ]

    def validate(self):
        if self.metric:
            self.metric = self.metric.strip().lower()
        if not self.metric:
            raise ValidationError('Metric name cannot be empty or just whitespace.')
        if self.limit <= 0:
            raise ValidationError('Limit must be a positive integer.')

    def save(self, *args, **kwargs):
        self.validate()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Limit Policy: {self.metric} (limit: {self.limit})"

class PlansLimitPolicies(models.Model):
    plan_id = models.ForeignKey(Plans, on_delete=models.CASCADE, related_name='plan_limit_policies')
    limit_policy_id = models.ForeignKey(LimitPolicies, on_delete=models.CASCADE, related_name='policy_plans')
    tenant_id = models.ForeignKey(Tenants, on_delete=models.CASCADE, related_name='plans_limit_policies')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('plan_id', 'limit_policy_id', 'tenant_id'),)
        indexes = [
            models.Index(fields=['plan_id'], name='plans_limit_policies_plan_idx'),
            models.Index(fields=['limit_policy_id'], name='plans_limit_policies_policy_idx'),
            models.Index(fields=['tenant_id'], name='plans_limit_policies_tenant_idx'),
        ]

    def validate(self):
        if self.plan_id and self.limit_policy_id and self.tenant_id:
            if self.plan_id.tenant_id != self.tenant_id:
                raise ValidationError('Plan must belong to the same tenant.')
            if self.limit_policy_id.tenant_id != self.tenant_id:
                raise ValidationError('Limit policy must belong to the same tenant.')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Plan: {self.plan_id.name} -> Policy: {self.limit_policy_id.metric}"


class Subscriptions(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(max_length=50, choices=SubscriptionsStatus.choices, default=SubscriptionsStatus.INACTIVE)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    subscribed_by = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='subscriptions')
    plan_id = models.ForeignKey(Plans, on_delete=models.CASCADE, related_name='subscriptions')
    tenant_id = models.ForeignKey(Tenants, on_delete=models.CASCADE, related_name='subscriptions')

    class Meta:
        db_table = 'subscriptions'
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
        unique_together = (('plan_id', 'tenant_id'),)
        indexes = [
            models.Index(fields=['status'], name='subscriptions_status_idx'),
            models.Index(fields=['subscribed_by'], name='subscriptions_subscribed_by_idx'),
            models.Index(fields=['plan_id'], name='subscriptions_plan_idx'),
            models.Index(fields=['tenant_id'], name='subscriptions_tenant_idx'),
            models.Index(fields=['started_at'], name='subscriptions_started_at_idx'),
        ]

    def validate(self):
        if self.plan_id and self.tenant_id:
            if self.plan_id.tenant_id != self.tenant_id:
                raise ValidationError('Plan must belong to the same tenant.')
        
        if self.ended_at and self.started_at and self.ended_at <= self.started_at:
            raise ValidationError('End date must be after start date.')

        if self.pk:
            old_instance = Subscriptions.objects.get(pk=self.pk)
            if old_instance.status == SubscriptionsStatus.CANCELLED and self.status == SubscriptionsStatus.ACTIVE:
                raise ValidationError('Cannot reactivate a cancelled subscription.')

    def save(self, *args, **kwargs):
        self.validate()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"Subscription: {self.plan_id.name} ({self.status})"
    
class Usages(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    metric = models.CharField(max_length=255)
    value = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    recorded_at = models.DateTimeField(auto_now_add=True)
    tenant_id = models.ForeignKey(Tenants, on_delete=models.CASCADE, related_name='usages')
    subscription_id = models.ForeignKey(Subscriptions, on_delete=models.CASCADE, related_name='usages')

    class Meta:
        db_table = 'usages'
        verbose_name = 'Usage'
        verbose_name_plural = 'Usages'
        indexes = [
            models.Index(fields=['metric'], name='usages_metric_idx'),
            models.Index(fields=['tenant_id'], name='usages_tenant_idx'),
            models.Index(fields=['subscription_id'], name='usages_subscription_idx'),
            models.Index(fields=['recorded_at'], name='usages_recorded_at_idx'),
            models.Index(fields=['metric', 'tenant_id', 'recorded_at'], name='usages_composite_idx'),
        ]

    def validate(self):
        if self.metric:
            self.metric = self.metric.strip().lower()
        if not self.metric:
            raise ValidationError('Metric name cannot be empty or just whitespace.') 
        if self.subscription_id and self.tenant_id:
            if self.subscription_id.tenant_id != self.tenant_id:
                raise ValidationError('Subscription must belong to the same tenant.')
        if self.value < 0:
            raise ValidationError('Usage value cannot be negative.')

    def save(self, *args, **kwargs):
        self.validate()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"Usage: {self.metric} = {self.value} (Subscription: {self.subscription_id.plan_id.name})"