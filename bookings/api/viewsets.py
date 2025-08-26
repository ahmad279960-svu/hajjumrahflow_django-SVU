# bookings/api/viewsets.py

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from bookings.models import Booking, Payment
from .serializers import BookingSerializer, PaymentSerializer

class BookingViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows bookings to be viewed.
    This is essential for n8n to fetch booking details for automation.
    """
    queryset = Booking.objects.all().select_related('customer', 'trip').order_by('-booking_date')
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def add_payment(self, request, pk=None):
        """
        A custom action to add a payment to a specific booking.
        Endpoint: /api/v1/bookings/{id}/add_payment/
        """
        booking = self.get_object()
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(booking=booking, recorded_by=request.user)
            booking.save() # Trigger signals or status updates on the booking
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing payments directly.
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]