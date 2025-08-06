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
    path('auth/register/user/', UserRegistrationView.as_view(), name='user_registration'),
    path('auth/register/tenant/', TenantRegistrationView.as_view(), name='tenant_registration'),
    path('auth/register/admin/', AdminRegistrationView.as_view(), name='admin_registration'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('plans/', PlanView.as_view(), name='plans_view'),
    path('plans/<uuid:pk>/', PlanView.as_view(), name='plan_detail'),
    path('limit-policies/', LimitPoliciesView.as_view(), name='limit_policies_view'),
    path('limit-policies/<uuid:pk>/', LimitPoliciesView.as_view(), name='limit_policy_detail'),
    path('plans-limit-policies/', PlanLimitPolicyView.as_view(), name='plans_limit_policies_view'),
    path('subscription/', SubscriptionView.as_view(), name='subscription_view'),
    path('subscription/<uuid:pk>/', SubscriptionView.as_view(), name='subscription_detail'),
]