# trips/forms.py

from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Trip, Expense

class TripForm(forms.ModelForm):
    """
    A form for creating and updating Trip instances.
    """
    class Meta:
        model = Trip
        fields = [
            'name', 'status', 'description', 'departure_date', 'return_date',
            'total_seats', 'price_per_person', 'hotel_details', 'flight_details'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'hotel_details': forms.Textarea(attrs={'rows': 3}),
            'flight_details': forms.Textarea(attrs={'rows': 3}),
            'departure_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'return_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if isinstance(field.widget, forms.CheckboxInput):
                 field.widget.attrs['class'] = 'form-check-input'

class ExpenseForm(forms.ModelForm):
    """
    A form for adding expenses to a trip.
    """
    class Meta:
        model = Expense
        fields = ['description', 'amount', 'expense_date']
        widgets = {
            'expense_date': forms.DateInput(attrs={'type': 'date'}),
        }