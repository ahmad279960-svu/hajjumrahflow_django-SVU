# bookings/urls.py

from django.urls import path
from .views import (
    BookingListView,
    BookingDetailView,
    AddPaymentView,
    BookingCreateWizardView,
    CheckSeatAvailabilityView,
)

app_name = 'bookings'

urlpatterns = [
    path('', BookingListView.as_view(), name='booking-list'),
    path('<int:pk>/', BookingDetailView.as_view(), name='booking-detail'),
    path('<int:booking_pk>/add-payment/', AddPaymentView.as_view(), name='add-payment'),

    # Booking Creation Wizard URLs
    path('create/step/<int:step>/', BookingCreateWizardView.as_view(), name='booking-create-step'),
    
    # HTMX URL
    path('htmx/check-seat-availability/', CheckSeatAvailabilityView.as_view(), name='check-seat-availability'),
]