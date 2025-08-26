# crm/api/serializers.py

from rest_framework import serializers
from crm.models import Customer, Document, CommunicationLog

class CustomerSerializer(serializers.ModelSerializer):
    """
    Serializer for the Customer model.
    Provides a comprehensive, read-only representation of a customer's data.
    """
    class Meta:
        model = Customer
        fields = [
            'id', 'full_name', 'phone_number', 'email', 'passport_number',
            'passport_expiry_date', 'nationality', 'date_of_birth',
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = fields # Make all fields read-only for now via API


class DocumentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Document model.
    """
    class Meta:
        model = Document
        fields = '__all__'


class CommunicationLogSerializer(serializers.ModelSerializer):
    """
    Serializer for the CommunicationLog model.
    This serializer is crucial for allowing n8n to log its activities.
    """
    class Meta:
        model = CommunicationLog
        fields = [
            'customer', 'channel', 'direction', 'content',
            'status', 'triggered_by'
        ]