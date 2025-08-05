from rest_framework import serializers
from django.core.exceptions import ValidationError
from .models import *
from .enums.role import Role
from .enums.limit_policies_metrics import LimitPoliciesMetrics
from .enums.subscriptions_status import SubscriptionsStatus
from .enums.subscriptions_billing_cycle import SubscriptionsBillingCycle
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password, check_password
from django.db import transaction

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id', 'email', 'name', 'role', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'role']
        write_only_fields = ['password']

class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenants
        fields = ['id', 'name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserTenantSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    tenant = TenantSerializer(read_only=True)

    class Meta:
        model = UserTenants
        fields = ['user', 'tenant', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class PlanSerializer(serializers.ModelSerializer):
    policy_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=True,
        help_text="List of limit policy IDs to associate with this plan"
    )

    class Meta:
        model = Plans
        fields = [
            'id', 
            'name', 
            'description', 
            'billing_cycle', 
            'billing_duration', 
            'price', 
            'created_at', 
            'updated_at', 
            'created_by',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_billing_cycle(self, value):
        if value not in SubscriptionsBillingCycle.values():
            raise ValidationError(f"Invalid billing cycle: {value}. Must be one of {SubscriptionsBillingCycle.values()}.")
        return value
    
    def validate_billing_duration(self, value):
        if value <= 0:
            raise ValidationError("Billing duration must be a positive integer.")
        return value
    
    def validate_price(self, value):
        if value < 0:
            raise ValidationError("Price must be a non-negative number.")
        return value
    
    @transaction.atomic
    def create(self, validated_data):
        policy_ids = validated_data.pop('policy_ids', [])
        plan = Plans.objects.create(**validated_data)
        
        for policy_id in policy_ids:
            try:
                limit_policy = LimitPolicies.objects.get(id=policy_id)
                PlansLimitPolicies.objects.create(plan=plan, limit_policy=limit_policy)
            except LimitPolicies.DoesNotExist:
                raise ValidationError(f"Limit policy with ID {policy_id} does not exist.")
        return plan

class LimitPoliciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = LimitPolicies
        fields = ['id', 'metric', 'limit', 'created_at', 'updated_at', 'created_by']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_metric(self, value):
        if value not in LimitPoliciesMetrics.values():
            raise ValidationError(f"Invalid metric: {value}. Must be one of {LimitPoliciesMetrics.values()}.")
        return value
    
    def validate_limit(self, value):
        if value <= 0:
            raise ValidationError("Limit must be a positive integer.")
        return value

class PlanLimitPolicySerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)
    limit_policy = LimitPoliciesSerializer(read_only=True)

    class Meta:
        model = PlansLimitPolicies
        fields = ['plan', 'limit_policy', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class SubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)
    tenant = TenantSerializer(read_only=True)

    class Meta:
        model = Subscriptions
        fields = ['id', 'plan', 'tenant', 'status', 'started_at', 'ended_at', 'created_at', 'updated_at', 'created_by_user_id']
        read_only_fields = ['id', 'created_at', 'updated_at']



class UsagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usages
        fields = ['id', 'metric', 'value', 'created_at', 'updated_at', 'subscription_id']
        read_only_fields = ['id', 'created_at', 'updated_at', 'subscription_id']

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'username' in self.fields:
            del self.fields['username']

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['id'] = str(user.id)
        return token

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        try:
            user = Users.objects.get(email=email)
        except Users.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password")
        
        if not check_password(password, user.password):
            raise serializers.ValidationError("Invalid email or password")
        
        refresh = self.get_token(user)
        
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


class UserRegistrationSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = Users
        fields = ['email', 'name', 'password', 'tenant_name']
        write_only_fields = ['password']
    
    def validate_tenant_name(self, value):
        if not value or not Tenants.objects.filter(name=value).exists():
            raise serializers.ValidationError("Tenant with this name does not exist")
        return value

    def validate_email(self, value):
        if value and Users.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists")
        return value

    @transaction.atomic
    def create(self, validated_data):
        try:
            tenant_name = validated_data.pop('tenant_name')
            validated_data['password'] = make_password(validated_data['password'])
            validated_data['role'] = Role.TENANT_USER
            user = Users.objects.create(**validated_data)
            tenant = Tenants.objects.get(name=tenant_name)
            UserTenants.objects.create(user=user, tenant=tenant)
            return user
        except Exception as e:
            raise serializers.ValidationError(f"Failed to create user {str(e)}")


class TenantRegistrationSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(required=True, write_only=True)
    
    class Meta:
        model = Users
        fields = ['email', 'name', 'password', 'tenant_name']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_tenant_name(self, value):
        if value and Tenants.objects.filter(name=value).exists():
            raise serializers.ValidationError("Tenant with this name already exists")
        return value

    def validate_email(self, value):
        if value and Users.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists")
        return value
    
    @transaction.atomic
    def create(self, validated_data):
        tenant_name = validated_data.pop('tenant_name')
        email = validated_data['email']
        
        if Users.objects.filter(email=email).exists():
            raise serializers.ValidationError("User with this email already exists")
        
        validated_data['password'] = make_password(validated_data['password'])
        validated_data['role'] = Role.TENANT_ADMIN 
        
        try:
            tenant = Tenants.objects.create(name=tenant_name)
            user = Users.objects.create(**validated_data)
            UserTenants.objects.create(user=user, tenant=tenant)
            return user
        except Exception as e:
            raise serializers.ValidationError(f"Failed to create tenant and user: {str(e)}")

class AdminRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['email', 'name', 'password']
        extra_kwargs = {'password': {'write_only': True}}
    
    def validate_email(self, value):
        if Users.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists")
        return value
    
    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        validated_data['role'] = Role.PLATFORM_ADMIN
        return Users.objects.create(**validated_data)
