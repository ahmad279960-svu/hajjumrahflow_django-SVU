# bookings/forms.py

from django import forms
from .models import Booking, Payment, Trip

class BookingForm(forms.ModelForm):
    """
    Form for creating a new booking. The wizard-style creation process
    will be handled in the view.
    """
    class Meta:
        model = Booking
        fields = ['customer', 'trip', 'total_amount']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['trip'].queryset = Trip.objects.filter(
            status__in=['scheduled', 'active']
        )
        self.fields['total_amount'].help_text = "Defaults to trip price, can be overridden."
    
    def clean(self):
        cleaned_data = super().clean()
        trip = cleaned_data.get("trip")
        if trip and trip.available_seats <= 0:
            self.add_error('trip', "There are no available seats for this trip.")
        return cleaned_data

class PaymentForm(forms.ModelForm):
    """
    Form for adding a new payment to an existing booking.
    """
    class Meta:
        model = Payment
        fields = ['amount_paid', 'payment_date', 'payment_method']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
        }