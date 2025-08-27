# core/views/public_views.py

from django.shortcuts import render, redirect
from django.views import View

class LandingPageView(View):
    """
    Renders the professional landing page for unauthenticated users.
    If a user is already authenticated, it redirects them to their dashboard.
    """
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return render(request, 'landing_page.html')