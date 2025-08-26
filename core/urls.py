# core/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views.authentication_views import CustomLoginView, CustomLogoutView
from .views.dashboard_views import DashboardView

urlpatterns = [
    # Admin Site
    path('admin/', admin.site.urls),

    # Core Views (Authentication & Dashboard)
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('', DashboardView.as_view(), name='dashboard'),

    # Application URLs
    path('crm/', include('crm.urls', namespace='crm')),
    path('trips/', include('trips.urls', namespace='trips')),
    path('bookings/', include('bookings.urls', namespace='bookings')),
    path('reports/', include('reports.urls', namespace='reports')),

    # API v1 URLs
    # This is the main entry point for all version 1 of our API.
    path('api/v1/', include([
        path('users/', include('users.urls', namespace='users_api')),
        path('crm/', include('crm.api.urls')),
        path('trips/', include('trips.api.urls')), # This line is now active
        path('bookings/', include('bookings.api.urls')), # This line is now active
    ])),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)