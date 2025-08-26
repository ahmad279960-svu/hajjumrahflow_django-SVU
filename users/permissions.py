# users/permissions.py

from rest_framework.permissions import BasePermission

class IsManager(BasePermission):
    """
    Allows access only to users with the 'manager' role.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'manager'

class IsAgent(BasePermission):
    """
    Allows access only to users with the 'agent' role.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'agent'

class IsAccountant(BasePermission):
    """
    Allows access only to users with the 'accountant' role.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'accountant'