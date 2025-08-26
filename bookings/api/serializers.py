# bookings/api/serializers.py

from rest_framework import serializers
from bookings.models import Booking, Payment
from crm.api.serializers import CustomerSerializer
from trips.api.serializers import TripSerializer

class PaymentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Payment model.
    """
    class Meta:
        model = Payment
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):
    """
    Serializer for the Booking model.
    Provides a nested representation of related customer and trip data.
    """
    # Nesting serializers provides more detailed, context-rich API responses.
    customer = CustomerSerializer(read_only=True)
    trip = TripSerializer(read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'customer', 'trip', 'status', 'total_amount', 'amount_paid',
            'balance_due', 'booking_date', 'created_by', 'last_reminder_sent_at',
            'payments'
        ]
        read_only_fields = fields