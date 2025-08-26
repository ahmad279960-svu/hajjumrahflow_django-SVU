# reports/services/financial_reports.py

from django.db.models import Sum
from bookings.models import Booking, Payment
from trips.models import Trip

class FinancialReportsGenerator:
    """
    A service class for generating financial-related reports.
    """
    @staticmethod
    def get_trip_profitability(trip):
        """
        Calculates the profitability of a single trip.
        Fulfills requirement 004-FR-REP.
        """
        bookings = Booking.objects.filter(trip=trip).exclude(status='cancelled')
        
        total_collected = Payment.objects.filter(booking__in=bookings).aggregate(
            total=Sum('amount_paid')
        )['total'] or 0

        total_expenses = trip.expenses.aggregate(
            total=Sum('amount')
        )['total'] or 0

        net_profit = total_collected - total_expenses

        return {
            'trip_name': trip.name,
            'total_revenue': total_collected,
            'total_expenses': total_expenses,
            'net_profit': net_profit,
        }

    @staticmethod
    def get_overdue_payments():
        """
        Retrieves a list of all bookings that are pending payment.
        Fulfills requirement 003-FR-REP.
        """
        # A more complex system might have due dates. For now, we list all
        # bookings that are in the 'pending_payment' status.
        return Booking.objects.filter(
            status=Booking.Status.PENDING_PAYMENT
        ).select_related('customer', 'trip').order_by('booking_date')