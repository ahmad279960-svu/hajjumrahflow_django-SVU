# users/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Customizes the admin interface for the CustomUser model.
    It displays the 'role' in the list view and adds it to the fieldsets
    for editing, making role management straightforward.
    """
    # Add 'role' to the list display in the admin panel
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'role')

    # Add 'role' to the fieldsets for the add/change forms
    # This inherits from the default UserAdmin fieldsets and adds our new field.
    fieldsets = UserAdmin.fieldsets + (
        ('Role Management', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role Management', {'fields': ('role',)}),
    )