# crm/management/commands/seed_data.py

import random
from datetime import timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from faker import Faker

from users.models import CustomUser
from crm.models import Customer
from trips.models import Trip, Expense
from bookings.models import Booking, Payment

class Command(BaseCommand):
    """
    A Django management command to seed the database with realistic sample data.
    This helps in testing and demonstrating the application's features.
    Usage: python manage.py seed_data
    """
    help = 'Seeds the database with initial data for testing and development.'

    def handle(self, *args, **options):
        if not CustomUser.objects.filter(is_superuser=True).exists():
            self.stdout.write(self.style.WARNING(
                'No superuser found. Please create a superuser first: '
                '`python manage.py createsuperuser`'
            ))
            return

        self.stdout.write("Starting database seeding process...")
        
        try:
            with transaction.atomic():
                self.clean_database()
                self.create_users()
                self.create_customers()
                self.create_trips()
                self.create_bookings_and_payments()
                self.create_expenses()

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {e}"))
            self.stdout.write(self.style.WARNING("Transaction rolled back. The database is in its previous state."))
            return

        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully! ✅'))

    def clean_database(self):
        """Deletes existing data to ensure a clean slate, preserving users."""
        self.stdout.write("Cleaning old data (excluding users)...")
        Payment.objects.all().delete()
        Booking.objects.all().delete()
        Expense.objects.all().delete()
        Trip.objects.all().delete()
        Customer.objects.filter(created_by__is_superuser=False).delete()


    def create_users(self):
        """Creates standard user roles if they don't exist."""
        self.stdout.write("Creating user roles...")
        
        users_to_create = [
            {'username': 'manager', 'role': CustomUser.Roles.MANAGER},
            {'username': 'agent', 'role': CustomUser.Roles.AGENT},
            {'username': 'accountant', 'role': CustomUser.Roles.ACCOUNTANT},
        ]

        for user_data in users_to_create:
            if not CustomUser.objects.filter(username=user_data['username']).exists():
                CustomUser.objects.create_user(
                    username=user_data['username'],
                    email=f"{user_data['username']}@hajjumrahflow.com",
                    password='password123',
                    role=user_data['role'],
                    is_staff=True 
                )
        self.users = CustomUser.objects.filter(is_superuser=False)


    def create_customers(self):
        """Creates a batch of fake customers."""
        self.stdout.write("Creating 250 customers...")
        fake = Faker()
        customers = []
        for _ in range(250):
            customers.append(Customer(
                full_name=fake.name(),
                phone_number=fake.unique.phone_number(),
                email=fake.unique.email(),
                passport_number=fake.unique.bothify(text='?#########').upper(),
                passport_expiry_date=fake.date_between(start_date='+1y', end_date='+10y'),
                nationality=fake.country(),
                date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=70),
                created_by=random.choice(self.users.filter(role=CustomUser.Roles.AGENT))
            ))
        Customer.objects.bulk_create(customers)
        self.customers = Customer.objects.all()

    def create_trips(self):
        """Creates a set of diverse trips."""
        self.stdout.write("Creating 15 trips...")
        fake = Faker()
        trip_names = [
            "Umrah Rajab 2026", "Hajj Premium 2026", "Ramadan Special Umrah",
            "Winter Break Umrah", "Eid al-Fitr Umrah Package", "VIP Hajj Experience 2027",
            "Economy Umrah - Spring", "Family Umrah Package", "10-Day Umrah Express",
            "Umrah Plus Al-Aqsa 2026", "Spiritual Journey Hajj 2026",
            "Short Umrah Getaway", "Golden Age Umrah (55+)", "New Year Umrah",
            "Completed Hajj 2025"
        ]
        
        trips = []
        for i, name in enumerate(trip_names):
            departure = timezone.now() + timedelta(days=random.randint(10, 365))
            return_date = departure + timedelta(days=random.randint(10, 25))
            status = random.choice([
                Trip.Status.SCHEDULED, Trip.Status.ACTIVE, Trip.Status.ACTIVE
            ])
            
            if i == len(trip_names) - 1: # Make the last one completed
                departure = timezone.now() - timedelta(days=60)
                return_date = departure + timedelta(days=20)
                status = Trip.Status.COMPLETED

            trips.append(Trip(
                name=name,
                description=fake.paragraph(nb_sentences=3),
                departure_date=departure,
                return_date=return_date,
                total_seats=random.randint(25, 100),
                price_per_person=random.randrange(1500, 8000, 100),
                status=status,
                hotel_details=f"5-star hotel near Haram: {fake.company()}",
                flight_details=f"Direct flight with {fake.company()} Airlines"
            ))
        Trip.objects.bulk_create(trips)
        self.trips = Trip.objects.filter(status__in=[Trip.Status.SCHEDULED, Trip.Status.ACTIVE])

    def create_bookings_and_payments(self):
        """Creates bookings for trips and adds payments to them."""
        self.stdout.write("Creating ~80 bookings and associated payments...")
        if not self.trips.exists():
            self.stdout.write(self.style.WARNING("No active or scheduled trips to create bookings for."))
            return
            
        bookings = []
        payments = []
        
        # Ensure we don't book the same customer twice on the same trip
        used_customer_trip_pairs = set()

        for _ in range(80):
            trip = random.choice(self.trips)
            customer = random.choice(self.customers)

            if (customer.id, trip.id) in used_customer_trip_pairs:
                continue
            
            if trip.available_seats > 0:
                booking = Booking(
                    customer=customer,
                    trip=trip,
                    created_by=random.choice(self.users.filter(role=CustomUser.Roles.AGENT)),
                    total_amount=trip.price_per_person,
                    status=random.choice([
                        Booking.Status.PENDING_DOCUMENTS,
                        Booking.Status.PENDING_PAYMENT,
                        Booking.Status.CONFIRMED,
                        Booking.Status.FULLY_PAID
                    ])
                )
                bookings.append(booking)
                used_customer_trip_pairs.add((customer.id, trip.id))

        # Bulk create bookings first to get IDs
        Booking.objects.bulk_create(bookings)
        
        # Now create payments based on the status of the created bookings
        for booking in Booking.objects.all():
            if booking.status == Booking.Status.CONFIRMED:
                # FIX: Convert the float from random.uniform to a Decimal before multiplication
                random_ratio = Decimal(str(random.uniform(0.2, 0.8)))
                amount = round(booking.total_amount * random_ratio, 2)
                payments.append(self.create_payment_instance(booking, amount))
            elif booking.status == Booking.Status.FULLY_PAID:
                payments.append(self.create_payment_instance(booking, booking.total_amount))

        Payment.objects.bulk_create(payments)


    def create_payment_instance(self, booking, amount):
        """Helper to create a Payment object instance."""
        return Payment(
            booking=booking,
            amount_paid=amount,
            payment_date=timezone.now().date() - timedelta(days=random.randint(1, 30)),
            payment_method=random.choice([
                Payment.PaymentMethod.BANK_TRANSFER,
                Payment.PaymentMethod.CASH,
                Payment.PaymentMethod.ONLINE
            ]),
            recorded_by=random.choice(self.users.filter(role__in=[CustomUser.Roles.AGENT, CustomUser.Roles.ACCOUNTANT]))
        )

    def create_expenses(self):
        """Creates random expenses for some of the trips."""
        self.stdout.write("Creating expenses for trips...")
        expenses = []
        all_trips = Trip.objects.all()
        for trip in all_trips:
            # Add 2 to 5 expense items per trip
            for _ in range(random.randint(2, 5)):
                expenses.append(Expense(
                    trip=trip,
                    description=random.choice(["Hotel Booking", "Flight Tickets", "Transportation", "Visa Fees", "Catering"]),
                    amount=random.randrange(5000, 20000, 500),
                    expense_date=trip.departure_date.date() - timedelta(days=random.randint(5, 20))
                ))
        Expense.objects.bulk_create(expenses)