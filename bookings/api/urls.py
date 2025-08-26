# bookings/api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import viewsets

router = DefaultRouter()
router.register(r'bookings', viewsets.BookingViewSet, basename='booking')
router.register(r'payments', viewsets.PaymentViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
]