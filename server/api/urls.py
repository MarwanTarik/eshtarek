from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserRegistrationView,
    TenantRegistrationView,
    AdminRegistrationView,
    LogoutView,
    LoginView,
)

urlpatterns = [
    path('auth/register/user/', UserRegistrationView.as_view(), name='user_registration'),
    path('auth/register/tenant/', TenantRegistrationView.as_view(), name='tenant_registration'),
    path('auth/register/admin/', AdminRegistrationView.as_view(), name='admin_registration'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/login/', LoginView.as_view(), name='login'),
]