# crm/api/viewsets.py

from rest_framework import viewsets, permissions
from crm.models import Customer, Document, CommunicationLog
from .serializers import CustomerSerializer, DocumentSerializer, CommunicationLogSerializer
from users.permissions import IsManager # We will use this later

class CustomerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows customers to be viewed.
    Access is restricted to authenticated staff users.
    """
    queryset = Customer.objects.all().order_by('-created_at')
    serializer_class = CustomerSerializer
    # permission_classes = [permissions.IsAuthenticated, IsManager] # Example for future permission


class DocumentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for viewing and managing customer documents.
    """
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    # permission_classes = [permissions.IsAuthenticated]


class CommunicationLogViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows n8n and other services to create communication log entries.
    This is a critical endpoint for automation workflows.
    """
    queryset = CommunicationLog.objects.all()
    serializer_class = CommunicationLogSerializer
    # For now, allow any authenticated user. In production, this might have a specific token.
    permission_classes = [permissions.IsAuthenticated]