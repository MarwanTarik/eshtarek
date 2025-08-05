from rest_framework.permissions import BasePermission
from .enums.role import Role

class IsAdmin(BasePermission):
    """
    Custom permission to only allow admin users to access the view.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        role = getattr(request.user, 'role', None) or (request.auth and request.auth.get('role'))
        return role == Role.PLATFORM_ADMIN

class IsTenantAdmin(BasePermission):
    """
    Custom permission to only allow tenant admin users to access the view.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        role = getattr(request.user, 'role', None) or (request.auth and request.auth.get('role'))
        return role == Role.TENANT_ADMIN


class IsTenantUser(BasePermission):
    """
    Custom permission to only allow tenant users to access the view.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        role = getattr(request.user, 'role', None) or (request.auth and request.auth.get('role'))
        return role == Role.TENANT_USER