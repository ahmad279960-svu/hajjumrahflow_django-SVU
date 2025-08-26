# crm/forms.py

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import Customer

class CustomerForm(forms.ModelForm):
    """
    A form for creating and updating Customer instances.
    It includes custom validation to prevent duplicate entries based on
    phone number or passport number.
    """
    class Meta:
        model = Customer
        fields = [
            'full_name', 'phone_number', 'email', 'passport_number',
            'passport_expiry_date', 'nationality', 'date_of_birth'
        ]
        # Use widgets to add HTML attributes like placeholders and to specify input types.
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': _('Enter full name')}),
            'phone_number': forms.TextInput(attrs={'placeholder': _('e.g., +963987654321')}),
            'email': forms.EmailInput(attrs={'placeholder': _('e.g., user@example.com')}),
            'passport_number': forms.TextInput(attrs={'placeholder': _('Enter passport number')}),
            'nationality': forms.TextInput(attrs={'placeholder': _('e.g., Syrian')}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'passport_expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_phone_number(self):
        """
        Ensures the phone number is unique.
        This check is case-insensitive and ignores existing instances during an update.
        """
        phone_number = self.cleaned_data.get('phone_number')
        # self.instance.pk is None for creation, and has a value for update.
        query = Customer.objects.filter(phone_number__iexact=phone_number)
        if self.instance.pk:
            query = query.exclude(pk=self.instance.pk)
        if query.exists():
            raise ValidationError(
                _("A customer with this phone number already exists."),
                code='duplicate_phone'
            )
        return phone_number

    def clean_passport_number(self):
        """
        Ensures the passport number is unique.
        """
        passport_number = self.cleaned_data.get('passport_number')
        query = Customer.objects.filter(passport_number__iexact=passport_number)
        if self.instance.pk:
            query = query.exclude(pk=self.instance.pk)
        if query.exists():
            raise ValidationError(
                _("A customer with this passport number already exists."),
                code='duplicate_passport'
            )
        return passport_number