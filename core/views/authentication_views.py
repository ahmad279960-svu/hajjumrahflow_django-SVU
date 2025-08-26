# core/views/authentication_views.py

from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy

class CustomLoginView(LoginView):
    """
    Handles user login.
    Uses a specific template for the login page and redirects
    the user to the main dashboard upon successful authentication.
    """
    template_name = 'login.html'
    redirect_authenticated_user = True
    next_page = reverse_lazy('dashboard')

class CustomLogoutView(LogoutView):
    """
    Handles user logout.
    Redirects the user to the login page after they have been logged out.
    """
    next_page = reverse_lazy('login')