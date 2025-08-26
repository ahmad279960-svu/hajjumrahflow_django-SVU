# trips/api/serializers.py

from rest_framework import serializers
from trips.models import Trip, Expense

class TripSerializer(serializers.ModelSerializer):
    """
    Serializer for the Trip model.
    Includes calculated properties for seat availability and occupancy.
    """
    # Make calculated fields available in the API
    available_seats = serializers.IntegerField(read_only=True)
    booked_seats = serializers.IntegerField(read_only=True)
    occupancy_rate = serializers.FloatField(read_only=True)

    class Meta:
        model = Trip
        fields = [
            'id', 'name', 'description', 'departure_date', 'return_date',
            'total_seats', 'price_per_person', 'status', 'hotel_details',
            'flight_details', 'booked_seats', 'available_seats', 'occupancy_rate',
            'created_at', 'updated_at'
        ]
        read_only_fields = fields


class ExpenseSerializer(serializers.ModelSerializer):
    """
    Serializer for the Expense model.
    Allows creating and viewing expenses related to a trip.
    """
    class Meta:
        model = Expense
        fields = '__all__'