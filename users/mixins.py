# users/mixins.py

from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied

class ManagerRequiredMixin(UserPassesTestMixin):
    """
    Ensures that the user accessing the view has the 'manager' role.
    """
    def test_func(self):
        if self.request.user.is_authenticated and self.request.user.role == 'manager':
            return True
        raise PermissionDenied

class AgentRequiredMixin(UserPassesTestMixin):
    """
    Ensures that the user accessing the view has the 'agent' role.
    Can be expanded to include managers if needed.
    """
    def test_func(self):
        if self.request.user.is_authenticated and (self.request.user.role == 'agent' or self.request.user.role == 'manager'):
            return True
        raise PermissionDenied

class AccountantRequiredMixin(UserPassesTestMixin):
    """
    Ensures that the user accessing the view has the 'accountant' role.
    """
    def test_func(self):
        if self.request.user.is_authenticated and (self.request.user.role == 'accountant' or self.request.user.role == 'manager'):
            return True
        raise PermissionDenied