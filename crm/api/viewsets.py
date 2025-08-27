# crm/api/viewsets.py

from rest_framework import viewsets, permissions
from crm.models import Customer, Document, CommunicationLog
from .serializers import CustomerSerializer, DocumentSerializer, CommunicationLogSerializer
from users.permissions import IsManager, IsAgent, IsAccountant

class CustomerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows customers to be viewed.
    Access is restricted based on user roles as per the permission matrix.
    Managers, Agents, and Accountants can view customer data.
    """
    queryset = Customer.objects.all().order_by('-created_at')
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated, IsManager | IsAgent | IsAccountant]


class DocumentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for viewing and managing customer documents.
    Accessible by Managers and Agents.
    """
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated, IsManager | IsAgent]


class CommunicationLogViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows n8n and other services to create communication log entries.
    This is a critical endpoint for automation workflows.
    It should only allow creation of new logs via the API for security.
    """
    queryset = CommunicationLog.objects.all()
    serializer_class = CommunicationLogSerializer
    # Only authenticated users (like our n8n service) can create logs.
    # Listing, updating, or deleting logs via this API is not a primary use case.
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['post', 'head', 'options'] # Restrict to POST only for creation