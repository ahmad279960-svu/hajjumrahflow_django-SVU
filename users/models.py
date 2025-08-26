# users/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    """
    Extends the default Django User model to include a role field.
    This is the central model for authentication and role-based permissions.
    """
    class Roles(models.TextChoices):
        MANAGER = 'manager', _('Manager')
        AGENT = 'agent', _('Agent')
        ACCOUNTANT = 'accountant', _('Accountant')

    # The 'email' field is promoted to be required and unique.
    email = models.EmailField(_('email address'), unique=True)

    # The 'role' field is essential for the RBAC system.
    role = models.CharField(
        _('role'),
        max_length=20,
        choices=Roles.choices,
        default=Roles.AGENT, # A safe default
        help_text=_('Designates the user\'s role within the system.')
    )

    def __str__(self):
        return self.username