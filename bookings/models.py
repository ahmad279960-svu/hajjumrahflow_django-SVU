# bookings/models.py

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class Booking(models.Model):
    """
    Represents a booking that links a Customer to a Trip.
    This is a central model that tracks the lifecycle of a customer's journey
    from initial reservation to final payment.
    """
    class Status(models.TextChoices):
        PENDING_DOCUMENTS = 'pending_documents', _('Pending Documents')
        PENDING_PAYMENT = 'pending_payment', _('Pending Payment')
        CONFIRMED = 'confirmed', _('Confirmed')
        FULLY_PAID = 'fully_paid', _('Fully Paid')
        CANCELLED = 'cancelled', _('Cancelled')

    customer = models.ForeignKey('crm.Customer', on_delete=models.CASCADE, related_name='bookings')
    trip = models.ForeignKey('trips.Trip', on_delete=models.CASCADE, related_name='bookings')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_bookings'
    )
    
    booking_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(_("Total Amount"), max_digits=10, decimal_places=2)
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING_DOCUMENTS
    )
    
    last_reminder_sent_at = models.DateTimeField(_("Last Reminder Sent"), null=True, blank=True)
    
    _original_status = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_status = self.status

    def __str__(self):
        return f"Booking for {self.customer.full_name} on {self.trip.name}"

    def clean(self):
        is_new = self.pk is None
        if is_new and self.trip.available_seats <= 0:
            raise ValidationError(_("There are no available seats for this trip."))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._original_status = self.status

    @property
    def amount_paid(self):
        return self.payments.aggregate(total=models.Sum('amount_paid'))['total'] or 0

    @property
    def balance_due(self):
        return self.total_amount - self.amount_paid

    def get_status_badge_class(self):
        """
        Returns a Bootstrap badge color class based on the booking status.
        """
        if self.status == self.Status.FULLY_PAID:
            return 'bg-success'
        elif self.status == self.Status.CONFIRMED:
            return 'bg-primary'
        elif self.status == self.Status.CANCELLED:
            return 'bg-danger'
        elif self.status == self.Status.PENDING_PAYMENT:
            return 'bg-warning'
        return 'bg-secondary' # Default for PENDING_DOCUMENTS etc.
        
    class Meta:
        verbose_name = _("Booking")
        verbose_name_plural = _("Bookings")
        ordering = ['-booking_date']


class Payment(models.Model):
    """
    Represents a single payment made towards a booking.
    """
    class PaymentMethod(models.TextChoices):
        CASH = 'cash', _('Cash')
        BANK_TRANSFER = 'bank_transfer', _('Bank Transfer')
        ONLINE = 'online', _('Online')

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    amount_paid = models.DecimalField(_("Amount Paid"), max_digits=10, decimal_places=2)
    payment_date = models.DateField(_("Payment Date"))
    payment_method = models.CharField(
        _("Payment Method"),
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CASH
    )
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recorded_payments'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment of {self.amount_paid} for {self.booking}"

    def clean(self):
        if self.amount_paid <= 0:
            raise ValidationError(_("Amount paid must be a positive number."))

    class Meta:
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")
        ordering = ['-payment_date']