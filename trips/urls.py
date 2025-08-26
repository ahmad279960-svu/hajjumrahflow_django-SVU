# trips/urls.py

from django.urls import path
from .views import (
    TripListView,
    TripDetailView,
    TripCreateView,
    TripUpdateView,
)

app_name = 'trips'

urlpatterns = [
    path('', TripListView.as_view(), name='trip-list'),
    path('create/', TripCreateView.as_view(), name='trip-create'),
    path('<int:pk>/', TripDetailView.as_view(), name='trip-detail'),
    path('<int:pk>/update/', TripUpdateView.as_view(), name='trip-update'),
]