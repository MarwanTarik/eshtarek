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
            'created_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class LimitPoliciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = LimitPolicies
        fields = ['id', 'metric', 'limit', 'created_at', 'updated_at', 'created_by']
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']


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
    
    def validate_tenant_name(self, data):
        tenant_name = data.get('tenant_name')
        if tenant_name and Tenants.objects.filter(name=tenant_name).exists():
            raise serializers.ValidationError("Tenant with this name already exists")
        return data

    def validate_email(self, data):
        email = data.get('email')
        if email and Users.objects.filter(email=email).exists():
            raise serializers.ValidationError("User with this email already exists")
        return data
    
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
    
    def validate_tenant_name(self, data):
        tenant_name = data.get('tenant_name')
        if tenant_name and Tenants.objects.filter(name=tenant_name).exists():
            raise serializers.ValidationError("Tenant with this name already exists")
        return data

    def validate_email(self, data):
        email = data.get('email')
        if email and Users.objects.filter(email=email).exists():
            raise serializers.ValidationError("User with this email already exists")
        return data
    
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
