# bookings/tests/test_models.py

import datetime
from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError

from crm.models import Customer
from trips.models import Trip
from users.models import CustomUser
from bookings.models import Booking, Payment

class BookingPaymentModelTest(TestCase):
    """
    Contains unit tests for the Booking and Payment models,
    ensuring their logic, properties, and relationships function correctly.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Set up a consistent environment for all tests in this class.
        This includes creating a user, a customer, and a trip.
        """
        cls.user = CustomUser.objects.create_user(username='testagent', role='agent')
        cls.customer = Customer.objects.create(
            full_name='Ahmed Khalid',
            phone_number='1234567890',
            passport_number='A12345678',
            passport_expiry_date=timezone.now().date() + datetime.timedelta(days=365 * 5),
            date_of_birth=timezone.now().date() - datetime.timedelta(days=365 * 30)
        )
        cls.trip = Trip.objects.create(
            name='Test Trip 2025',
            departure_date=timezone.now() + datetime.timedelta(days=60),
            return_date=timezone.now() + datetime.timedelta(days=70),
            total_seats=10,
            price_per_person=5000.00
        )

    def test_booking_creation_and_defaults(self):
        """
        Tests that a Booking is created with the correct initial status
        and that financial properties are calculated correctly at the start.
        """
        booking = Booking.objects.create(
            customer=self.customer,
            trip=self.trip,
            created_by=self.user,
            total_amount=self.trip.price_per_person
        )
        self.assertEqual(booking.status, Booking.Status.PENDING_DOCUMENTS)
        self.assertEqual(booking.total_amount, 5000.00)
        self.assertEqual(booking.amount_paid, 0)
        self.assertEqual(booking.balance_due, 5000.00)
        self.assertEqual(str(booking), f"Booking for {self.customer.full_name} on {self.trip.name}")

    def test_payment_updates_balance_due(self):
        """
        Ensures that creating a Payment correctly updates the
        amount_paid and balance_due properties of the associated Booking.
        """
        booking = Booking.objects.create(
            customer=self.customer,
            trip=self.trip,
            total_amount=5000.00,
            created_by=self.user
        )
        Payment.objects.create(
            booking=booking,
            amount_paid=1500.00,
            payment_date=timezone.now().date(),
            recorded_by=self.user
        )
        self.assertEqual(booking.amount_paid, 1500.00)
        self.assertEqual(booking.balance_due, 3500.00)

        Payment.objects.create(
            booking=booking,
            amount_paid=500.00,
            payment_date=timezone.now().date(),
            recorded_by=self.user
        )
        self.assertEqual(booking.amount_paid, 2000.00)
        self.assertEqual(booking.balance_due, 3000.00)

    def test_payment_cannot_be_zero_or_negative(self):
        """
        Validates that a Payment with a zero or negative amount
        raises a ValidationError.
        """
        booking = Booking.objects.create(
            customer=self.customer,
            trip=self.trip,
            total_amount=5000.00,
            created_by=self.user
        )
        with self.assertRaises(ValidationError):
            payment = Payment(booking=booking, amount_paid=0, payment_date=timezone.now().date())
            payment.full_clean() # full_clean() is required to trigger model validation

        with self.assertRaises(ValidationError):
            payment = Payment(booking=booking, amount_paid=-100, payment_date=timezone.now().date())
            payment.full_clean()

    def test_get_status_badge_class(self):
        """
        Tests the helper method for returning correct Bootstrap badge classes
        based on the booking status.
        """
        booking = Booking(status=Booking.Status.PENDING_DOCUMENTS)
        self.assertEqual(booking.get_status_badge_class(), 'bg-secondary')

        booking.status = Booking.Status.PENDING_PAYMENT
        self.assertEqual(booking.get_status_badge_class(), 'bg-warning')

        booking.status = Booking.Status.CONFIRMED
        self.assertEqual(booking.get_status_badge_class(), 'bg-primary')

        booking.status = Booking.Status.FULLY_PAID
        self.assertEqual(booking.get_status_badge_class(), 'bg-success')

        booking.status = Booking.Status.CANCELLED
        self.assertEqual(booking.get_status_badge_class(), 'bg-danger')