# trips/models.py

from django.db import models
from django.db.models import Sum
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

class Trip(models.Model):
    """
    Represents a Hajj or Umrah trip package.
    This is a central model that holds all details about a specific trip,
    including dates, pricing, and capacity.
    """
    class Status(models.TextChoices):
        SCHEDULED = 'scheduled', _('Scheduled') # Planned but not yet open for booking
        ACTIVE = 'active', _('Active')       # Open for booking
        COMPLETED = 'completed', _('Completed')   # The trip has finished
        CANCELLED = 'cancelled', _('Cancelled')   # The trip has been cancelled

    name = models.CharField(_("Trip Name"), max_length=255)
    description = models.TextField(_("Description"), null=True, blank=True)
    departure_date = models.DateTimeField(_("Departure Date"))
    return_date = models.DateTimeField(_("Return Date"))
    total_seats = models.PositiveIntegerField(_("Total Seats"))
    price_per_person = models.DecimalField(_("Price per Person"), max_digits=10, decimal_places=2)
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED
    )

    # These fields can store unstructured details about the trip package.
    hotel_details = models.TextField(_("Hotel Details"), null=True, blank=True)
    flight_details = models.TextField(_("Flight Details"), null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.departure_date.strftime('%Y-%m-%d')})"

    # Requirement 002-FR-TRP: Dynamic properties for seat calculation
    @property
    def booked_seats(self):
        """
        Calculates the number of confirmed and paid seats.
        It excludes cancelled bookings.
        """
        return self.bookings.exclude(status='cancelled').count()

    @property
    def available_seats(self):
        """
        Calculates the number of seats still available for booking.
        """
        return self.total_seats - self.booked_seats

    @property
    def occupancy_rate(self):
        """
        Calculates the percentage of seats that have been booked.
        """
        if self.total_seats == 0:
            return 0
        return (self.booked_seats / self.total_seats) * 100

    def get_total_collected(self):
        """
        Calculates the sum of all payments for all non-cancelled bookings on this trip.
        """
        return self.bookings.exclude(status='cancelled').aggregate(
            total=Sum('payments__amount_paid')
        )['total'] or 0
        
    def get_total_expenses(self):
        """
        Calculates the sum of all recorded expenses for this trip.
        """
        return self.expenses.aggregate(total=Sum('amount'))['total'] or 0

    def clean(self):
        """
        Adds model-level validation.
        """
        if self.departure_date and self.return_date and self.return_date <= self.departure_date:
            raise ValidationError(_("Return date must be after the departure date."))
        if self.total_seats is not None and self.total_seats < 0:
            raise ValidationError(_("Total seats cannot be negative."))
        
    class Meta:
        verbose_name = _("Trip")
        verbose_name_plural = _("Trips")
        ordering = ['departure_date']


class Expense(models.Model):
    """
    Represents an operational expense associated with a specific trip.
    This is used to calculate the trip's profitability.
    """
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='expenses')
    description = models.CharField(_("Description"), max_length=255)
    amount = models.DecimalField(_("Amount"), max_digits=10, decimal_places=2)
    expense_date = models.DateField(_("Date of Expense"), default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.description} ({self.amount}) for {self.trip.name}"

    class Meta:
        verbose_name = _("Expense")
        verbose_name_plural = _("Expenses")
        ordering = ['-expense_date']