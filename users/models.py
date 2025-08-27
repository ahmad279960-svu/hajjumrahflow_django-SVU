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

    # FIX: Added unique related_name to resolve system check errors (E304).
    # This prevents clashes with the default auth.User model's reverse accessors.
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="customuser_set",  # Unique related_name
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="customuser_set",  # Unique related_name
        related_query_name="user",
    )

    def __str__(self):
        return self.username