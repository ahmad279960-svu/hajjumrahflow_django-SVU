# core/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from .views.authentication_views import CustomLoginView, CustomLogoutView
from .views.dashboard_views import DashboardView
from .views.public_views import LandingPageView

# These patterns will not be prefixed with language code
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include([
        path('users/', include('users.urls', namespace='users_api')),
        path('crm/', include('crm.api.urls')),
        path('trips/', include('trips.api.urls')),
        path('bookings/', include('bookings.api.urls')),
    ])),
    path('api/v1/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/v1/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/v1/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('i18n/', include('django.conf.urls.i18n')), # Language switcher URL
    path('logout/', CustomLogoutView.as_view(), name='logout'), # Moved for consistency
]

# These patterns will be prefixed with the language code (e.g., /ar/dashboard/)
urlpatterns += i18n_patterns(
    path('', LandingPageView.as_view(), name='landing-page'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),

    # Application URLs
    path('crm/', include('crm.urls', namespace='crm')),
    path('trips/', include('trips.urls', namespace='trips')),
    path('bookings/', include('bookings.urls', namespace='bookings')),
    path('reports/', include('reports.urls', namespace='reports')),
    
    prefix_default_language=False
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)