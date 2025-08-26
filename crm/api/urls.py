# crm/api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import viewsets

# The router automatically generates the URL patterns for the viewsets.
router = DefaultRouter()
router.register(r'customers', viewsets.CustomerViewSet, basename='customer')
router.register(r'documents', viewsets.DocumentViewSet, basename='document')
router.register(r'communication-logs', viewsets.CommunicationLogViewSet, basename='communicationlog')

urlpatterns = [
    # The generated URLs will be included under this path.
    # e.g., /api/v1/crm/customers/
    path('', include(router.urls)),
]