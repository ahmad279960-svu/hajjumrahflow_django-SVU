# crm/tests/test_forms.py

from django.test import TestCase
from crm.forms import CustomerForm
from crm.models import Customer
import datetime

class CustomerFormTest(TestCase):
    """
    This class contains unit tests for the CustomerForm,
    focusing on its custom validation logic for preventing duplicates.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Create a pre-existing customer to test against for duplicates.
        """
        Customer.objects.create(
            full_name='Existing User',
            phone_number='987654321',
            passport_number='P98765',
            passport_expiry_date=datetime.date(2030, 1, 1),
            date_of_birth=datetime.date(1990, 1, 1)
        )

    def test_form_is_valid_with_correct_data(self):
        """
        Test that the form is valid when provided with unique and correct data.
        """
        form_data = {
            'full_name': 'Jane Doe',
            'phone_number': '1234567890',
            'passport_number': 'B87654321',
            'passport_expiry_date': '2032-02-02',
            'nationality': 'Testlandia',
            'date_of_birth': '1992-02-02'
        }
        form = CustomerForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_is_invalid_with_missing_required_fields(self):
        """
        Test that the form is invalid if required fields are missing.
        """
        form = CustomerForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('full_name', form.errors)
        self.assertIn('phone_number', form.errors)
        self.assertIn('passport_number', form.errors)

    def test_form_rejects_duplicate_phone_number(self):
        """
        Test the custom validation to ensure a duplicate phone number is rejected.
        """
        form_data = {
            'full_name': 'Another User',
            'phone_number': '987654321', # Duplicate phone
            'passport_number': 'P111222',
            'passport_expiry_date': '2031-01-01',
            'nationality': 'Newland',
            'date_of_birth': '1991-01-01'
        }
        form = CustomerForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('phone_number', form.errors)
        self.assertEqual(form.errors['phone_number'][0], 'A customer with this phone number already exists.')

    def test_form_rejects_duplicate_passport_number(self):
        """
        Test the custom validation to ensure a duplicate passport number is rejected.
        """
        form_data = {
            'full_name': 'Third User',
            'phone_number': '555555555',
            'passport_number': 'P98765', # Duplicate passport
            'passport_expiry_date': '2033-01-01',
            'nationality': 'Oldland',
            'date_of_birth': '1993-01-01'
        }
        form = CustomerForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('passport_number', form.errors)
        self.assertEqual(form.errors['passport_number'][0], 'A customer with this passport number already exists.')