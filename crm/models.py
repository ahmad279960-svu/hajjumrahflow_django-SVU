# crm/models.py

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Customer(models.Model):
    """
    Represents a customer (pilgrim) in the system.
    This model stores all personal and contact information.
    """
    full_name = models.CharField(_("Full Name"), max_length=255)
    phone_number = models.CharField(_("Phone Number"), max_length=20, unique=True)
    email = models.EmailField(_("Email Address"), unique=True, null=True, blank=True)
    passport_number = models.CharField(_("Passport Number"), max_length=50, unique=True)
    passport_expiry_date = models.DateField(_("Passport Expiry Date"))
    nationality = models.CharField(_("Nationality"), max_length=100)
    date_of_birth = models.DateField(_("Date of Birth"))

    # Foreign key to the user who created this customer record.
    # ON_DELETE=models.SET_NULL means if the employee user is deleted,
    # the customer record is kept but no longer associated with that employee.
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_customers'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} ({self.passport_number})"

    class Meta:
        verbose_name = _("Customer")
        verbose_name_plural = _("Customers")
        ordering = ['-created_at']


class Document(models.Model):
    """
    Represents a document uploaded for a customer.
    e.g., Passport copy, personal photo.
    """
    class DocumentType(models.TextChoices):
        PASSPORT_COPY = 'passport_copy', _('Passport Copy')
        PERSONAL_PHOTO = 'personal_photo', _('Personal Photo')
        OTHER = 'other', _('Other')

    class DocumentStatus(models.TextChoices):
        REQUIRED = 'required', _('Required')
        UPLOADED = 'uploaded', _('Uploaded')
        VERIFIED = 'verified', _('Verified')

    # Each document must be linked to a customer.
    # ON_DELETE=models.CASCADE means if a customer is deleted, all their documents are also deleted.
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(_("Document Type"), max_length=20, choices=DocumentType.choices)
    
    # It's good practice to organize uploads into subdirectories.
    file = models.FileField(_("File"), upload_to='customer_documents/%Y/%m/')
    status = models.CharField(_("Status"), max_length=20, choices=DocumentStatus.choices, default=DocumentStatus.UPLOADED)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_document_type_display()} for {self.customer.full_name}"

    class Meta:
        verbose_name = _("Document")
        verbose_name_plural = _("Documents")


class CommunicationLog(models.Model):
    """
    Logs all automated communications sent to a customer via n8n.
    This provides a complete audit trail of interactions.
    """
    class ChannelType(models.TextChoices):
        EMAIL = 'email', _('Email')
        WHATSAPP = 'whatsapp', _('WhatsApp')
        SMS = 'sms', _('SMS')

    class DirectionType(models.TextChoices):
        OUTGOING = 'outgoing', _('Outgoing')
        INCOMING = 'incoming', _('Incoming')
        
    class StatusType(models.TextChoices):
        SENT = 'sent', _('Sent')
        DELIVERED = 'delivered', _('Delivered')
        FAILED = 'failed', _('Failed')

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='communication_logs')
    channel = models.CharField(_("Channel"), max_length=20, choices=ChannelType.choices)
    direction = models.CharField(_("Direction"), max_length=10, choices=DirectionType.choices, default=DirectionType.OUTGOING)
    content = models.TextField(_("Content"))
    status = models.CharField(_("Status"), max_length=20, choices=StatusType.choices)
    triggered_by = models.CharField(_("Triggered By"), max_length=255, help_text=_("e.g., 'New Booking Onboarding Workflow'"))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_channel_display()} to {self.customer.full_name} at {self.created_at}"

    class Meta:
        verbose_name = _("Communication Log")
        verbose_name_plural = _("Communication Logs")
        ordering = ['-created_at']