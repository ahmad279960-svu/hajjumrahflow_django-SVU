# reports/urls.py

from django.urls import path
from .views import (
    ReportDashboardView,
    GenerateManifestView,
    TripProfitabilityView
)

app_name = 'reports'

urlpatterns = [
    path('', ReportDashboardView.as_view(), name='dashboard'),
    path('generate/manifest/', GenerateManifestView.as_view(), name='generate-manifest'),
    path('profitability/', TripProfitabilityView.as_view(), name='trip-profitability'),
]