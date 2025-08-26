# crm/admin.py

from django.contrib import admin
from .models import Customer, Document, CommunicationLog

class DocumentInline(admin.TabularInline):
    """
    Allows managing documents directly from the customer's admin page.
    This provides a much more intuitive admin experience.
    """
    model = Document
    extra = 1 # Show one extra blank form for adding a new document
    readonly_fields = ('uploaded_at',)

class CommunicationLogInline(admin.TabularInline):
    """
    Shows a read-only log of communications on the customer's admin page.
    This is useful for quick reference by admins.
    """
    model = CommunicationLog
    extra = 0
    readonly_fields = ('channel', 'content', 'status', 'triggered_by', 'created_at')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """
    Customizes the admin interface for the Customer model.
    """
    inlines = [DocumentInline, CommunicationLogInline]
    list_display = ('full_name', 'phone_number', 'passport_number', 'nationality', 'created_by')
    search_fields = ('full_name', 'phone_number', 'passport_number', 'email')
    list_filter = ('nationality', 'created_at')
    readonly_fields = ('created_at', 'updated_at')

    # Organizes the fields in the detail view for better readability.
    fieldsets = (
        (None, {
            'fields': ('full_name', 'phone_number', 'email')
        }),
        ('Personal Information', {
            'fields': ('date_of_birth', 'nationality')
        }),
        ('Passport Details', {
            'fields': ('passport_number', 'passport_expiry_date')
        }),
        ('System Information', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',) # Make this section collapsible
        }),
    )

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """
    Admin view for Documents.
    """
    list_display = ('customer', 'document_type', 'status', 'uploaded_at')
    list_filter = ('document_type', 'status')
    search_fields = ('customer__full_name', 'customer__passport_number')