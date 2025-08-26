# trips/tests/test_models.py

from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
import datetime

from trips.models import Trip
from crm.models import Customer
from users.models import CustomUser
from bookings.models import Booking

class TripModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        Set up non-modified objects used by all test methods.
        This is run once for the entire class.
        """
        cls.user = CustomUser.objects.create_user(username='testagent', role='agent')
        cls.customer1 = Customer.objects.create(
            full_name='Test Customer One',
            phone_number='111111',
            passport_number='P111',
            passport_expiry_date=timezone.now().date() + datetime.timedelta(days=365 * 2),
            date_of_birth=timezone.now().date() - datetime.timedelta(days=365 * 30)
        )
        cls.customer2 = Customer.objects.create(
            full_name='Test Customer Two',
            phone_number='222222',
            passport_number='P222',
            passport_expiry_date=timezone.now().date() + datetime.timedelta(days=365 * 3),
            date_of_birth=timezone.now().date() - datetime.timedelta(days=365 * 40)
        )
        
        departure = timezone.now() + datetime.timedelta(days=30)
        return_date = departure + datetime.timedelta(days=10)

        cls.trip = Trip.objects.create(
            name='Umrah Ramadhan 2026',
            departure_date=departure,
            return_date=return_date,
            total_seats=10,
            price_per_person=2500.00
        )
        
        # Create a couple of bookings for occupancy tests
        Booking.objects.create(customer=cls.customer1, trip=cls.trip, total_amount=2500.00, created_by=cls.user)
        Booking.objects.create(customer=cls.customer2, trip=cls.trip, total_amount=2500.00, created_by=cls.user)

    def test_trip_creation(self):
        """
        Tests that a Trip instance was created successfully via setUpTestData.
        """
        self.assertEqual(self.trip.name, 'Umrah Ramadhan 2026')
        self.assertEqual(self.trip.total_seats, 10)

    def test_occupancy_properties(self):
        """
        Tests the dynamic calculation of booked seats, available seats, and occupancy rate.
        """
        self.assertEqual(self.trip.booked_seats, 2)
        self.assertEqual(self.trip.available_seats, 8)
        self.assertEqual(self.trip.occupancy_rate, 20.0) # (2 / 10) * 100

    def test_cancellation_updates_occupancy(self):
        """
        Tests that cancelling a booking correctly updates the occupancy.
        """
        booking_to_cancel = Booking.objects.get(customer=self.customer1)
        booking_to_cancel.status = Booking.Status.CANCELLED
        booking_to_cancel.save()
        
        # Refresh the trip instance from the database to get the latest state
        self.trip.refresh_from_db()

        self.assertEqual(self.trip.booked_seats, 1)
        self.assertEqual(self.trip.available_seats, 9)
        self.assertEqual(self.trip.occupancy_rate, 10.0)

    def test_validation_return_date_before_departure(self):
        """
        Tests that the model prevents saving if the return date is before the departure date.
        """
        departure = timezone.now() + datetime.timedelta(days=5)
        invalid_return = departure - datetime.timedelta(days=1)
        
        with self.assertRaises(ValidationError):
            trip_with_error = Trip(
                name='Invalid Trip',
                departure_date=departure,
                return_date=invalid_return,
                total_seats=5,
                price_per_person=100
            )
            trip_with_error.full_clean() # full_clean() must be called to trigger validation