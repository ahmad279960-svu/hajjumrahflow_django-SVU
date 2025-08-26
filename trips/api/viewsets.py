# trips/api/viewsets.py

from rest_framework import viewsets, permissions
from trips.models import Trip, Expense
from .serializers import TripSerializer, ExpenseSerializer
from users.permissions import IsManager

class TripViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows trips to be viewed.
    Access is restricted to authenticated staff users.
    """
    queryset = Trip.objects.all().order_by('-departure_date')
    serializer_class = TripSerializer
    permission_classes = [permissions.IsAuthenticated]


class ExpenseViewSet(viewsets.ModelViewSet):
    """
    API endpoint for viewing and managing trip expenses.
    Access should be limited to Managers and Accountants in a real scenario.
    """
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated, IsManager]