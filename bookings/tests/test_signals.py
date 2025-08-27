# bookings/tests/test_signals.py

import datetime
from unittest.mock import patch
from django.test import TestCase
from django.utils import timezone

from crm.models import Customer
from trips.models import Trip
from users.models import CustomUser
from bookings.models import Booking, Payment

class BookingSignalsTest(TestCase):
    """
    Contains tests to ensure that Django signals related to the bookings app
    are firing correctly and triggering the expected webhooks.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Set up a consistent environment for all signal tests.
        """
        cls.user = CustomUser.objects.create_user(username='testagent', role='agent')
        cls.customer = Customer.objects.create(
            full_name='Signal Test Customer',
            phone_number='9876543210',
            passport_number='P98765',
            passport_expiry_date=timezone.now().date() + datetime.timedelta(days=365 * 5),
            date_of_birth=timezone.now().date() - datetime.timedelta(days=365 * 25)
        )
        cls.trip = Trip.objects.create(
            name='Signal Test Trip',
            departure_date=timezone.now() + datetime.timedelta(days=90),
            return_date=timezone.now() + datetime.timedelta(days=100),
            total_seats=5,
            price_per_person=1000.00
        )

    @patch('bookings.signals.requests.post')
    def test_new_booking_webhook_is_sent(self, mock_post):
        """
        Tests that creating a new Booking triggers the `trigger_new_booking_workflow`
        signal and that `requests.post` is called with the correct data.
        """
        # Create a new booking, which should fire the signal
        Booking.objects.create(
            customer=self.customer,
            trip=self.trip,
            created_by=self.user,
            total_amount=self.trip.price_per_person
        )

        # Assert that requests.post was called exactly once
        mock_post.assert_called_once()

        # Get the arguments with which requests.post was called
        args, kwargs = mock_post.call_args
        
        # Check that the payload is correct
        self.assertIn('json', kwargs)
        payload = kwargs['json']
        self.assertEqual(payload['customer_id'], self.customer.id)
        self.assertEqual(payload['trip_id'], self.trip.id)

    @patch('bookings.signals.requests.post')
    def test_new_payment_webhook_is_sent(self, mock_post):
        """
        Tests that creating a new Payment triggers the `handle_new_payment`
        signal and sends the correct webhook.
        """
        booking = Booking.objects.create(
            customer=self.customer,
            trip=self.trip,
            total_amount=self.trip.price_per_person
        )

        # Create a new payment, which should fire the signal
        Payment.objects.create(
            booking=booking,
            amount_paid=500.00,
            payment_date=timezone.now().date(),
            recorded_by=self.user
        )

        # The signal for booking creation is also called, so we check the last call
        self.assertTrue(mock_post.called)
        
        # Get the arguments of the LAST call to requests.post
        args, kwargs = mock_post.call_args
        
        self.assertIn('json', kwargs)
        payload = kwargs['json']
        self.assertEqual(payload['booking_id'], booking.id)
        self.assertEqual(payload['customer_id'], self.customer.id)