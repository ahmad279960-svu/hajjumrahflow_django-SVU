# crm/tests/test_models.py

# This file is for unit tests related to the CRM models.
# Tests should cover model creation, relationships, and any custom methods.

from django.test import TestCase
from users.models import CustomUser
from crm.models import Customer

# class CustomerModelTest(TestCase):
#
#     @classmethod
#     def setUpTestData(cls):
#         # Set up non-modified objects used by all test methods
#         user = CustomUser.objects.create_user(username='testuser', password='password123')
#         Customer.objects.create(
#             full_name='John Doe',
#             phone_number='1234567890',
#             passport_number='A12345678',
#             passport_expiry_date='2030-01-01',
#             nationality='Testland',
#             date_of_birth='1990-01-01',
#             created_by=user
#         )
#
#     def test_full_name_label(self):
#         customer = Customer.objects.get(id=1)
#         field_label = customer._meta.get_field('full_name').verbose_name
#         self.assertEqual(field_label, 'Full Name')