# users/views.py

from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from .models import CustomUser
from .serializers import UserSerializer

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A read-only API endpoint that allows users to be viewed.
    Access is restricted to admin users for security.
    """
    queryset = CustomUser.objects.all().order_by('id')
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser] # Only admins can list users via API