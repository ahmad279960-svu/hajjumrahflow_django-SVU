# bookings/admin.py

from django.contrib import admin
from .models import Booking, Payment

class PaymentInline(admin.TabularInline):
    """
    Allows managing payments directly from the booking's admin page.
    """
    model = Payment
    extra = 1
    readonly_fields = ('created_at', 'recorded_by')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """
    Customizes the admin interface for the Booking model.
    """
    inlines = [PaymentInline]
    list_display = ('id', 'customer', 'trip', 'status', 'total_amount', 'amount_paid', 'balance_due', 'booking_date')
    list_filter = ('status', 'trip')
    search_fields = ('customer__full_name', 'customer__passport_number', 'trip__name')
    readonly_fields = ('amount_paid', 'balance_due', 'booking_date')
    
    fieldsets = (
        (None, {
            'fields': ('customer', 'trip', 'status')
        }),
        ('Financials', {
            'fields': ('total_amount', 'amount_paid', 'balance_due')
        }),
        ('System Info', {
            'fields': ('created_by', 'booking_date', 'last_reminder_sent_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk: # If creating a new booking
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    Admin view for Payments.
    """
    list_display = ('booking', 'amount_paid', 'payment_date', 'payment_method', 'recorded_by')
    search_fields = ('booking__customer__full_name', 'booking__trip__name')
    list_filter = ('payment_method', 'payment_date')

    def save_model(self, request, obj, form, change):
        if not obj.pk: # If creating a new payment
            obj.recorded_by = request.user
        super().save_model(request, obj, form, change)