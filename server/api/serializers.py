from rest_framework import serializers
from django.core.exceptions import ValidationError
from .models import *
from .enums.role import Role
from .enums.limit_policies_metrics import LimitPoliciesMetrics
from .enums.subscriptions_status import SubscriptionsStatus

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id', 'email', 'name', 'role', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['email', 'name', 'role', 'password']
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {'password': {'write_only': True}}
    
    def validate_role(self, value):
        if value not in [choice[0] for choice in Role.choices]:
            raise serializers.ValidationError(f"Invalid role. Must be one of: {[choice[0] for choice in Role.choices]}")
        return value

class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['email', 'name']
        read_only_fields = ['id', 'created_at', 'updated_at']

class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenants
        fields = ['id', 'name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class CreateTenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenants
        fields = ['name']
        read_only_fields = ['id', 'created_at', 'updated_at']

class UpdateTenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenants
        fields = ['name']
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserTenantSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    tenant = TenantSerializer(read_only=True)

    class Meta:
        model = UserTenants
        fields = ['user', 'tenant', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class CreateUserTenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTenants
        fields = ['user', 'tenant']
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {'user': {'required': True}, 'tenant': {'required': True}}

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plans
        fields = ['id', 'name', 'description', 'billing_cycle', 'billing_duration', 'price', 'created_at', 'updated_at', 'created_by']
        read_only_fields = ['id', 'created_at', 'updated_at']

class CreatePlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plans
        fields = ['name', 'price', 'description', 'billing_cycle', 'billing_duration', 'created_by']
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {'price': {'required': True}}
    
    def validate_billing_cycle(self, value):
        valid_cycles = [choice[0] for choice in SubscriptionsBillingCycle.choices]
        if value not in valid_cycles:
            raise serializers.ValidationError(f"Invalid billing cycle. Must be one of: {valid_cycles}")
        return value
    
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value

class UpdatePlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plans
        fields = ['name', 'price', 'description', 'billing_cycle', 'billing_duration']
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {'price': {'required': True}}

class LimitPoliciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = LimitPolicies
        fields = ['id', 'metric', 'limit', 'created_at', 'updated_at', 'created_by']
        read_only_fields = ['id', 'created_at', 'updated_at']

class CreateLimitPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = LimitPolicies
        fields = ['metric', 'limit', 'created_by']
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {'limit': {'required': True}}
    
    def validate_metric(self, value):
        if value not in [choice[0] for choice in LimitPoliciesMetrics.choices]:
            raise serializers.ValidationError(f"Invalid metric. Must be one of: {[choice[0] for choice in LimitPoliciesMetrics.choices]}")
        return value
    
    def validate_limit(self, value):
        if value <= 0:
            raise serializers.ValidationError("Limit must be greater than 0")
        return value

class UpdateLimitPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = LimitPolicies
        fields = ['metric', 'limit']
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {'limit': {'required': True}}

class PlanLimitPolicySerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)
    limit_policy = LimitPoliciesSerializer(read_only=True)

    class Meta:
        model = PlansLimitPolicies
        fields = ['plan', 'limit_policy', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class CreatePlanLimitPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = PlansLimitPolicies
        fields = ['plan', 'limit_policy']
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {'plan': {'required': True}, 'limit_policy': {'required': True}}

class SubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)
    tenant = TenantSerializer(read_only=True)

    class Meta:
        model = Subscriptions
        fields = ['id', 'plan', 'tenant', 'status', 'started_at', 'ended_at', 'created_at', 'updated_at', 'created_by_user_id']
        read_only_fields = ['id', 'created_at', 'updated_at']

class CreateSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscriptions
        fields = ['plan_id', 'tenant_id', 'status', 'started_at', 'ended_at', 'created_by_user_id']
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {'status': {'required': True}, 'started_at': {'required': True}, 'ended_at': {'required': True}}
    
    def validate_status(self, value):
        if value not in [choice[0] for choice in SubscriptionsStatus.choices]:
            raise serializers.ValidationError(f"Invalid status. Must be one of: {[choice[0] for choice in SubscriptionsStatus.choices]}")
        return value
    
    def validate(self, data):
        if data.get('started_at') and data.get('ended_at'):
            if data['started_at'] >= data['ended_at']:
                raise serializers.ValidationError("End date must be after start date")
        return data


class UpdateSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscriptions
        fields = ['status', 'started_at', 'ended_at', 'plan_id']
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {'status': {'required': True}, 'started_at': {'required': True}, 'ended_at': {'required': True}, 'plan_id': {'required': True}}

class UsagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usages
        fields = ['id', 'metric', 'value', 'created_at', 'updated_at', 'subscription_id']
        read_only_fields = ['id', 'created_at', 'updated_at', 'subscription_id']

class CreateUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usages
        fields = ['metric', 'value', 'subscription_id']
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {'metric': {'required': True}, 'value': {'required': True}, 'subscription_id': {'required': True}}
    
    def validate_metric(self, value):
        if value not in [choice[0] for choice in LimitPoliciesMetrics.choices]:
            raise serializers.ValidationError(f"Invalid metric. Must be one of: {[choice[0] for choice in LimitPoliciesMetrics.choices]}")
        return value
    
    def validate_value(self, value):
        if value < 0:
            raise serializers.ValidationError("Value must be non-negative")
        return value

class UpdateUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usages
        fields = ['metric', 'value']
        read_only_fields = ['id', 'created_at', 'updated_at', 'subscription_id']
        extra_kwargs = {'metric': {'required': True}, 'value': {'required': True}}

