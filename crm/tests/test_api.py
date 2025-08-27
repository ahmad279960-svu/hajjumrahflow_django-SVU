# crm/tests/test_api.py

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from users.models import CustomUser
from crm.models import Customer

class CrmApiTests(APITestCase):
    """
    Integration tests for the CRM API endpoints.
    These tests ensure the API behaves as expected, checking status codes,
    data formats, authentication, and permissions.
    """

    @classmethod
    def setUpTestData(cls):
        # Create users with different roles
        cls.manager = CustomUser.objects.create_user(username='manager', password='password123', role='manager')
        cls.agent = CustomUser.objects.create_user(username='agent', password='password123', role='agent')
        cls.accountant = CustomUser.objects.create_user(username='accountant', password='password123', role='accountant')

        # Create tokens for authentication
        cls.manager_token = Token.objects.create(user=cls.manager)
        cls.agent_token = Token.objects.create(user=cls.agent)
        cls.accountant_token = Token.objects.create(user=cls.accountant)

        # Create a sample customer
        Customer.objects.create(
            full_name='Test Customer',
            phone_number='123456789',
            passport_number='P12345',
            passport_expiry_date='2030-01-01',
            date_of_birth='1990-01-01'
        )
        cls.customer_list_url = reverse('customer-list')

    def test_customer_list_unauthenticated(self):
        """
        Ensure unauthenticated users cannot access the customer list.
        """
        response = self.client.get(self.customer_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_manager_can_list_customers(self):
        """
        Ensure a manager can successfully list customers.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.manager_token.key)
        response = self.client.get(self.customer_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1) # Check if one customer is returned

    def test_agent_can_list_customers(self):
        """
        Ensure an agent can successfully list customers.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.agent_token.key)
        response = self.client.get(self.customer_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_accountant_can_list_customers(self):
        """
        Ensure an accountant can successfully list customers (read-only access).
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.accountant_token.key)
        response = self.client.get(self.customer_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)