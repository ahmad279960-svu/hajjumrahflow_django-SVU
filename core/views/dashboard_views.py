# core/views/dashboard_views.py

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.db.models import Sum, Count, Q
from django.utils import timezone
import datetime
import json

from bookings.models import Booking, Payment
from trips.models import Trip, Expense # FIX: Added 'Expense' to the import list
from crm.models import Customer

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
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        
        # Key Performance Indicators (KPIs)
        total_revenue_month = Payment.objects.filter(
            payment_date__gte=start_of_month
        ).aggregate(total=Sum('amount_paid'))['total'] or 0

        new_bookings_month = Booking.objects.filter(
            booking_date__gte=start_of_month
        ).count()
        
        active_trips_count = Trip.objects.filter(status=Trip.Status.ACTIVE).count()
        total_customers_count = Customer.objects.count()

        # Data for the occupancy chart: Get top 5 upcoming trips
        upcoming_trips = Trip.objects.filter(
            departure_date__gte=today,
            status__in=[Trip.Status.SCHEDULED, Trip.Status.ACTIVE]
        ).order_by('departure_date')[:5]

        chart_labels = [trip.name for trip in upcoming_trips]
        chart_data = [round(trip.occupancy_rate, 2) for trip in upcoming_trips]

        # Recent Activity
        recent_bookings = Booking.objects.order_by('-booking_date')[:5]

        return {
            'total_revenue_month': f"{total_revenue_month:,.2f}",
            'new_bookings_month': new_bookings_month,
            'active_trips_count': active_trips_count,
            'total_customers_count': total_customers_count,
            'chart_labels': json.dumps(chart_labels),
            'chart_data': json.dumps(chart_data),
            'recent_bookings': recent_bookings,
        }

    def get_agent_context(self):
        """
        Gathers and returns context data for the Agent dashboard.
        """
        agent = self.request.user
        
        # KPIs for the specific agent
        my_bookings_today = Booking.objects.filter(
            created_by=agent,
            booking_date__date=timezone.now().date()
        ).count()
        
        my_total_bookings = Booking.objects.filter(created_by=agent).count()

        # Actionable Lists
        pending_docs_bookings = Booking.objects.filter(
            created_by=agent,
            status=Booking.Status.PENDING_DOCUMENTS
        ).select_related('customer', 'trip')[:5]

        pending_payment_bookings = Booking.objects.filter(
            created_by=agent,
            status=Booking.Status.PENDING_PAYMENT
        ).select_related('customer', 'trip')[:5]

        return {
            'my_bookings_today': my_bookings_today,
            'my_total_bookings': my_total_bookings,
            'pending_docs_bookings': pending_docs_bookings,
            'pending_payment_bookings': pending_payment_bookings,
        }

    def get_accountant_context(self):
        """
        Gathers and returns context data for the Accountant dashboard.
        """
        today = timezone.now().date()

        # KPIs
        collected_today = Payment.objects.filter(
            payment_date=today
        ).aggregate(total=Sum('amount_paid'))['total'] or 0

        overdue_payments_count = Booking.objects.filter(
            status=Booking.Status.PENDING_PAYMENT
        ).count()

        total_expenses_month = Expense.objects.filter(
            expense_date__gte=today.replace(day=1)
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Recent Transactions
        recent_payments = Payment.objects.select_related(
            'booking__customer', 'recorded_by'
        ).order_by('-payment_date', '-created_at')[:10]

        return {
            'collected_today': f"{collected_today:,.2f}",
            'overdue_payments_count': overdue_payments_count,
            'total_expenses_month': f"{total_expenses_month:,.2f}",
            'recent_payments': recent_payments,
        }