# bookings/tests/test_workflow.py

from django.test import TestCase
from django.utils import timezone
import datetime

from crm.models import Customer
from trips.models import Trip
from users.models import CustomUser
from bookings.models import Booking, Payment

class BookingWorkflowTest(TestCase):
    """
    This class contains integration tests that simulate a complete user workflow,
    ensuring that all apps (crm, trips, bookings) work together correctly.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Set up the necessary objects for the entire test class.
        """
        cls.user = CustomUser.objects.create_user(username='testagent', role='agent')
        cls.customer = Customer.objects.create(
            full_name='John Doe',
            phone_number='1234567890',
            passport_number='A12345678',
            passport_expiry_date=timezone.now().date() + datetime.timedelta(days=365 * 5),
            date_of_birth=timezone.now().date() - datetime.timedelta(days=365 * 30)
        )
        cls.trip = Trip.objects.create(
            name='Test Workflow Trip',
            departure_date=timezone.now() + datetime.timedelta(days=60),
            return_date=timezone.now() + datetime.timedelta(days=70),
            total_seats=20,
            price_per_person=5000.00
        )

    def test_full_booking_to_payment_workflow(self):
        """
        Tests the entire lifecycle of a booking:
        1. Create a Booking and verify seat reduction.
        2. Record a partial Payment and verify status change and balance.
        3. Record the final Payment and verify status change to 'Fully Paid'.
        """
        # 1. Initial state check
        self.assertEqual(self.trip.available_seats, 20)
        self.assertEqual(self.trip.booked_seats, 0)

        # 2. Create a new booking
        booking = Booking.objects.create(
            customer=self.customer,
            trip=self.trip,
            created_by=self.user,
            total_amount=self.trip.price_per_person,
            status=Booking.Status.PENDING_PAYMENT # Start with pending payment
        )
        self.trip.refresh_from_db()
        self.assertEqual(self.trip.available_seats, 19, "Seat should be deducted after booking.")
        self.assertEqual(self.trip.booked_seats, 1)
        self.assertEqual(booking.balance_due, 5000.00)

        # 3. Record a partial payment
        # This will trigger the post_save signal in bookings/signals.py
        Payment.objects.create(
            booking=booking,
            amount_paid=2000.00,
            payment_date=timezone.now().date(),
            recorded_by=self.user
        )
        booking.refresh_from_db()
        self.assertEqual(booking.balance_due, 3000.00, "Balance should be updated after partial payment.")
        self.assertEqual(booking.status, Booking.Status.CONFIRMED, "Status should change to Confirmed after first payment.")

        # 4. Record the final payment
        Payment.objects.create(
            booking=booking,
            amount_paid=3000.00,
            payment_date=timezone.now().date(),
            recorded_by=self.user
        )
        booking.refresh_from_db()
        self.assertEqual(booking.balance_due, 0.00, "Balance should be zero after full payment.")
        self.assertEqual(booking.status, Booking.Status.FULLY_PAID, "Status should change to Fully Paid.")

    def test_cancellation_workflow(self):
        """
        Tests the cancellation process:
        1. Create a booking.
        2. Cancel the booking.
        3. Verify that the seat is released and available again on the Trip.
        """
        # 1. Create a booking
        booking = Booking.objects.create(
            customer=self.customer,
            trip=self.trip,
            created_by=self.user,
            total_amount=self.trip.price_per_person,
        )
        self.trip.refresh_from_db()
        self.assertEqual(self.trip.available_seats, 19)

        # 2. Cancel the booking
        booking.status = Booking.Status.CANCELLED
        booking.save() # Trigger the save method logic
        
        self.trip.refresh_from_db()
        
        # 3. Verify seat is released
        self.assertEqual(self.trip.available_seats, 20, "Seat should be released after cancellation.")
        self.assertEqual(self.trip.booked_seats, 0)