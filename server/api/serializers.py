from datetime import timedelta
from django.utils import timezone
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
from django.db import IntegrityError

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
        write_only=True,
        help_text="List of limit policy IDs to associate with this plan"
    )
    
    associated_policy_ids = serializers.SerializerMethodField(read_only=True)
    associated_policies = serializers.SerializerMethodField(read_only=True)

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
            'policy_ids',
            'associated_policy_ids',
            'associated_policies',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']

    def get_associated_policy_ids(self, obj):
        return [str(plp.limit_policy.id) for plp in obj.plan_limit_policies.all()]
    
    def get_associated_policies(self, obj):
        policies = [plp.limit_policy for plp in obj.plan_limit_policies.select_related('limit_policy').all()]
        return LimitPoliciesSerializer(policies, many=True).data

    def validate_billing_cycle(self, value):
        valid_choices = [choice[0] for choice in SubscriptionsBillingCycle.choices]
        if value not in valid_choices:
            raise ValidationError(f"Invalid billing cycle: {value}. Must be one of {valid_choices}.")
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
        if not self.context['request'].user.is_authenticated:
            raise serializers.ValidationError("Authentication required")
        
        policy_ids = validated_data.pop('policy_ids', [])
        user_id = self.context['request'].user.id

        plan = Plans.objects.create(**validated_data, created_by_id=user_id)
      
        for policy_id in policy_ids:
            try:
                limit_policy = LimitPolicies.objects.get(id=policy_id)
                try:
                    PlansLimitPolicies.objects.create(plan=plan, limit_policy=limit_policy)
                except IntegrityError:
                    raise ValidationError(f"Plan limit policy association already exists for plan {plan.id} and policy {policy_id}.")
            except LimitPolicies.DoesNotExist:
                raise ValidationError(f"Limit policy with ID {policy_id} does not exist.")
        return plan

    @transaction.atomic  
    def update(self, instance, validated_data):
        policy_ids = validated_data.pop('policy_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if policy_ids is not None:
            instance.plan_limit_policies.all().delete()
            
            for policy_id in policy_ids:
                try:
                    limit_policy = LimitPolicies.objects.get(id=policy_id)
                    try:
                        PlansLimitPolicies.objects.create(plan=instance, limit_policy=limit_policy)
                    except IntegrityError:
                        raise ValidationError(f"Plan limit policy association already exists for plan {instance.id} and policy {policy_id}.")
                except LimitPolicies.DoesNotExist:
                    raise ValidationError(f"Limit policy with ID {policy_id} does not exist.")
        
        return instance

class LimitPoliciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = LimitPolicies
        fields = ['id', 'metric', 'limit', 'created_at', 'updated_at', 'created_by']
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']
    
    def validate_limit(self, value):
        if value <= 0:
            raise ValidationError("Limit must be a positive integer.")
        return value
    
    @transaction.atomic
    def create(self, validated_data):
        if not self.context['request'].user.is_authenticated:
            raise serializers.ValidationError("Authentication required")
        
        user_id = self.context['request'].user.id
        
        try:
            limit_policy = LimitPolicies.objects.create(**validated_data, created_by_id=user_id)
        except IntegrityError:
            raise serializers.ValidationError("Limit policy with this metric already exists.")
        
        return limit_policy

class PlanLimitPolicySerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)
    limit_policy = LimitPoliciesSerializer(read_only=True)
    plan_id = serializers.UUIDField(write_only=True)
    policy_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = PlansLimitPolicies
        fields = ['plan', 'limit_policy', 'plan_id', 'policy_id', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def create(self, validated_data):
        plan_id = validated_data.pop('plan_id')
        policy_id = validated_data.pop('policy_id')
        
        try:
            plan = Plans.objects.get(id=plan_id)
            limit_policy = LimitPolicies.objects.get(id=policy_id)
        except Plans.DoesNotExist:
            raise serializers.ValidationError(f"Plan with ID {plan_id} does not exist.")
        except LimitPolicies.DoesNotExist:
            raise serializers.ValidationError(f"Limit policy with ID {policy_id} does not exist.")
        
        if PlansLimitPolicies.objects.filter(plan=plan, limit_policy=limit_policy).exists():
            raise serializers.ValidationError(f"Plan limit policy association already exists for plan {plan_id} and policy {policy_id}.")
        
        try:
            with transaction.atomic():
                plan_limit_policy = PlansLimitPolicies.objects.create(
                    plan=plan,
                    limit_policy=limit_policy
                )
        except IntegrityError:
            raise serializers.ValidationError(f"Plan limit policy association already exists for plan {plan_id} and policy {policy_id}.")
        
        return plan_limit_policy

class SubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)
    tenant = TenantSerializer(read_only=True)
    plan_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Subscriptions
        fields = [
            'id', 
            'plan', 
            'tenant', 
            'status', 
            'started_at', 
            'ended_at', 
            'created_at', 
            'updated_at', 
            'created_by_user_id',
            'plan_id'
        ]
        read_only_fields = [
            'id', 
            'created_at', 
            'updated_at', 
            'created_by_user_id', 
            'status', 
            'started_at', 
            'ended_at',
            'tenant',
        ]

    def validate_status(self, value):
        valid_choices = [choice[0] for choice in SubscriptionsStatus.choices]
        if value not in valid_choices:
            raise ValidationError(f"Invalid status: {value}. Must be one of {valid_choices}.")
        return value
    
    @transaction.atomic
    def create(self, validated_data):
        if not self.context['request'].user.is_authenticated:
            raise serializers.ValidationError("Authentication required")
        
        plan_id = validated_data.pop('plan_id')
        user_id = self.context['request'].user.id
        tenant_id = UserTenants.objects.get(user_id=user_id).tenant.id

        try:
            plan = Plans.objects.get(id=plan_id)
            tenant = Tenants.objects.get(id=tenant_id)
        except Plans.DoesNotExist:
            raise serializers.ValidationError(f"Plan with ID {plan_id} does not exist.")
        except Tenants.DoesNotExist:
            raise serializers.ValidationError(f"Tenant with ID {tenant_id} does not exist.")
        
        if Subscriptions.objects.filter(plan=plan, tenant=tenant).exists():
            raise serializers.ValidationError(f"Subscription already exists for plan {plan_id} and tenant {tenant_id}.")
        
    
        started_at = timezone.now()
        if plan.billing_cycle == SubscriptionsBillingCycle.ANNUALLY:
            ended_at = started_at + timedelta(days=365 * plan.billing_duration)
        elif plan.billing_cycle == SubscriptionsBillingCycle.MONTHLY:
            ended_at = started_at + timedelta(weeks=4 * plan.billing_duration)
        else:
            raise serializers.ValidationError(f"Invalid billing cycle: {plan.billing_cycle}")

        subscription = Subscriptions.objects.create(
            plan=plan,
            tenant=tenant,
            status=SubscriptionsStatus.ACTIVE,
            created_by_user_id=tenant_id,
            started_at=started_at,
            ended_at=ended_at,
            **validated_data
        )
        return subscription
    
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
        token['email'] = user.email
        token['name'] = user.name
        token['created_at'] = user.created_at.isoformat() if user.created_at else None
        token['updated_at'] = user.updated_at.isoformat() if user.updated_at else None
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

