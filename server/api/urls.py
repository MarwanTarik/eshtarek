from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserRegistrationView,
    TenantRegistrationView,
    AdminRegistrationView,
    LogoutView,
    LoginView,
    PlanView,
    LimitPoliciesView,
    PlanLimitPolicyView,
    SubscriptionView,
)

urlpatterns = [
    path('user/auth/register/', UserRegistrationView.as_view(), name='user_registration'),
    path('tenant/auth/register/', TenantRegistrationView.as_view(), name='tenant_registration'),
    path('admin/auth/register/', AdminRegistrationView.as_view(), name='admin_registration'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('plans/', PlanView.as_view(), name='plans_view'),
    path('plans/<uuid:pk>/', PlanView.as_view(), name='plan_detail'),
    path('limit-policies/', LimitPoliciesView.as_view(), name='limit_policies_view'),
    path('limit-policies/<uuid:pk>/', LimitPoliciesView.as_view(), name='limit_policy_detail'),
    path('plans-limit-policies/', PlanLimitPolicyView.as_view(), name='plans_limit_policies_view'),
    path('subscriptions/', SubscriptionView.as_view(), name='subscription_view'),
    path('subscriptions/<uuid:pk>/', SubscriptionView.as_view(), name='subscription_detail'),
]