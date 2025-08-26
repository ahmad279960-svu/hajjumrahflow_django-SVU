# core/views/dashboard_views.py

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.db.models import Sum, Count
from django.utils import timezone
import datetime
import json

from bookings.models import Booking, Payment
from trips.models import Trip

class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Dynamically renders the appropriate dashboard based on the user's role.
    This view acts as a gatekeeper and data provider for the main landing page
    after a user logs in.
    """
    def get_template_names(self):
        user_role = getattr(self.request.user, 'role', None)
        if user_role == 'manager':
            return ['dashboards/manager_dashboard.html']
        elif user_role == 'agent':
            return ['dashboards/agent_dashboard.html']
        elif user_role == 'accountant':
            return ['dashboards/accountant_dashboard.html']
        else:
            # Fallback for superusers or users without a defined role
            return ['dashboards/default_dashboard.html']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_role = getattr(self.request.user, 'role', None)

        if user_role == 'manager':
            context.update(self.get_manager_context())
        elif user_role == 'agent':
            context.update(self.get_agent_context())
        elif user_role == 'accountant':
            context.update(self.get_accountant_context())

        return context

    def get_manager_context(self):
        """
        Gathers and returns the context data required for the Manager dashboard.
        """
        today = timezone.now()
        start_of_week = today - datetime.timedelta(days=today.weekday())
        
        total_revenue = Payment.objects.filter(
            payment_date__year=today.year,
            payment_date__month=today.month
        ).aggregate(total=Sum('amount_paid'))['total'] or 0

        new_bookings_week = Booking.objects.filter(
            booking_date__gte=start_of_week
        ).count()

        active_trips = Trip.objects.filter(status='active').count()

        # Data for the occupancy chart: Get top 5 upcoming trips
        upcoming_trips = Trip.objects.filter(
            departure_date__gte=today,
            status__in=['scheduled', 'active']
        ).order_by('departure_date')[:5]

        chart_labels = [trip.name for trip in upcoming_trips]
        chart_data = [round(trip.occupancy_rate, 2) for trip in upcoming_trips]

        return {
            'total_revenue': f"{total_revenue:,.2f}",
            'new_bookings_week': new_bookings_week,
            'active_trips': active_trips,
            'chart_labels': json.dumps(chart_labels),
            'chart_data': json.dumps(chart_data),
        }

    def get_agent_context(self):
        """
        Gathers and returns context data for the Agent dashboard.
        """
        my_new_bookings_today = Booking.objects.filter(
            created_by=self.request.user,
            booking_date__date=timezone.now().date()
        ).count()
        
        pending_documents_count = Booking.objects.filter(
            status=Booking.Status.PENDING_DOCUMENTS
        ).count()

        return {
            'my_new_bookings_today': my_new_bookings_today,
            'pending_documents_count': pending_documents_count
        }

    def get_accountant_context(self):
        """
        Gathers and returns context data for the Accountant dashboard.
        """
        collected_today = Payment.objects.filter(
            payment_date=timezone.now().date()
        ).aggregate(total=Sum('amount_paid'))['total'] or 0

        overdue_payments_count = Booking.objects.filter(
            status=Booking.Status.PENDING_PAYMENT
        ).count()

        return {
            'collected_today': f"{collected_today:,.2f}",
            'overdue_payments_count': overdue_payments_count
        }