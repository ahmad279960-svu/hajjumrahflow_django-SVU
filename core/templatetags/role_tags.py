# core/templatetags/role_tags.py

from django import template

register = template.Library()

@register.filter(name='has_role')
def has_role(user, role_name):
    """
    A template filter to check if a user has a specific role.
    Usage: {% if request.user|has_role:'manager' %} ... {% endif %}
    """
    return user.is_authenticated and user.role == role_name