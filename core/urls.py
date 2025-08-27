# core/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views.authentication_views import CustomLoginView, CustomLogoutView
from .views.dashboard_views import DashboardView
from .views.public_views import LandingPageView # This line should now work correctly

urlpatterns = [
    # Admin Site
    path('admin/', admin.site.urls),

    # Public and Authentication Views
    path('', LandingPageView.as_view(), name='landing-page'), # Root URL is now the landing page
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'), # Dashboard is now at /dashboard/

    # Application URLs
    path('crm/', include('crm.urls', namespace='crm')),
    path('trips/', include('trips.urls', namespace='trips')),
    path('bookings/', include('bookings.urls', namespace='bookings')),
    path('reports/', include('reports.urls', namespace='reports')),

    # API v1 URLs
    path('api/v1/', include([
        path('users/', include('users.urls', namespace='users_api')),
        path('crm/', include('crm.api.urls')),
        path('trips/', include('trips.api.urls')),
        path('bookings/', include('bookings.api.urls')),
    ])),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)