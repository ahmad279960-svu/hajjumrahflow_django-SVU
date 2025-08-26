# trips/api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import viewsets

router = DefaultRouter()
router.register(r'trips', viewsets.TripViewSet, basename='trip')
router.register(r'expenses', viewsets.ExpenseViewSet, basename='expense')

urlpatterns = [
    path('', include(router.urls)),
]