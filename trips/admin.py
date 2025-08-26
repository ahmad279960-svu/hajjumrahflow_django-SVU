# trips/admin.py

from django.contrib import admin
from .models import Trip, Expense

class ExpenseInline(admin.TabularInline):
    """
    Allows managing expenses directly from the trip's admin page.
    """
    model = Expense
    extra = 1

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    """
    Customizes the admin interface for the Trip model.
    """
    inlines = [ExpenseInline]
    list_display = ('name', 'departure_date', 'status', 'total_seats', 'booked_seats', 'available_seats', 'occupancy_rate_display')
    list_filter = ('status', 'departure_date')
    search_fields = ('name',)
    
    # Fields to be displayed in the detail view.
    # The readonly_fields are for our custom @property methods.
    readonly_fields = ('booked_seats', 'available_seats', 'occupancy_rate')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'status', 'description')
        }),
        ('Dates & Capacity', {
            'fields': ('departure_date', 'return_date', 'total_seats', 'price_per_person')
        }),
        ('Package Details', {
            'fields': ('hotel_details', 'flight_details'),
            'classes': ('collapse',)
        }),
        ('Calculated Metrics', {
            'fields': ('booked_seats', 'available_seats', 'occupancy_rate'),
             'classes': ('collapse',)
        }),
    )

    @admin.display(description='Occupancy')
    def occupancy_rate_display(self, obj):
        return f"{obj.occupancy_rate:.2f}%"

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    """
    Admin view for Expenses.
    """
    list_display = ('trip', 'description', 'amount', 'expense_date')
    search_fields = ('trip__name', 'description')
    list_filter = ('expense_date',)