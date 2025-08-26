# trips/views.py

from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.contrib import messages

from .models import Trip
from .forms import TripForm
from bookings.models import Booking
from users.mixins import ManagerRequiredMixin

class TripListView(LoginRequiredMixin, ListView):
    """
    Displays a list of all trips. Allows filtering by trip status.
    Accessible by all authenticated users.
    """
    model = Trip
    template_name = 'trips/trip_list.html'
    context_object_name = 'trips'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get('status')
        if status in [s[0] for s in Trip.Status.choices]:
            queryset = queryset.filter(status=status)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_status'] = self.request.GET.get('status', '')
        context['trip_statuses'] = Trip.Status.choices
        return context

class TripDetailView(LoginRequiredMixin, DetailView):
    """
    Provides a comprehensive financial and administrative summary for a single trip.
    This view fulfills the requirements of 004-FR-TRP.
    """
    model = Trip
    template_name = 'trips/trip_detail.html'
    context_object_name = 'trip'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        trip = self.get_object()

        # Get all non-cancelled bookings for this trip.
        registered_travelers = trip.bookings.exclude(status='cancelled')
        
        # Financial Calculations are now handled by methods on the Trip model itself.
        total_collected = trip.get_total_collected()
        total_expenses = trip.get_total_expenses()
        net_profit = total_collected - total_expenses
        expected_revenue = trip.price_per_person * trip.booked_seats
        
        context['registered_travelers'] = registered_travelers
        context['financial_summary'] = {
            'expected_revenue': expected_revenue,
            'total_collected': total_collected,
            'total_expenses': total_expenses,
            'net_profit': net_profit
        }
        return context

class TripCreateView(LoginRequiredMixin, ManagerRequiredMixin, CreateView):
    """
    Handles the creation of a new trip. Restricted to Managers.
    """
    model = Trip
    form_class = TripForm
    template_name = 'trips/trip_form.html'
    success_url = reverse_lazy('trips:trip-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _("Create New Trip")
        return context
    
    def form_valid(self, form):
        messages.success(self.request, _("Trip has been created successfully."))
        return super().form_valid(form)

class TripUpdateView(LoginRequiredMixin, ManagerRequiredMixin, UpdateView):
    """
    Handles updating an existing trip. Restricted to Managers.
    """
    model = Trip
    form_class = TripForm
    template_name = 'trips/trip_form.html'
    
    def get_success_url(self):
        return reverse_lazy('trips:trip-detail', kwargs={'pk': self.object.pk})
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _("Update Trip")
        return context

    def form_valid(self, form):
        messages.success(self.request, _("Trip has been updated successfully."))
        return super().form_valid(form)