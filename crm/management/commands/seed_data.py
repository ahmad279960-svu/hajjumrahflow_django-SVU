# crm/management/commands/seed_data.py

import random
from datetime import timedelta, date, datetime
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
    A Django management command to seed the database with a large and realistic
    sample dataset for better model training and application demonstration.
    Usage: python manage.py seed_data
    """
    help = 'Seeds the database with a large, enhanced dataset.'

    # --- CONFIGURATION ---
    NUM_CUSTOMERS = 1000
    NUM_TRIPS = 50
    NUM_BOOKINGS = 600
    # --- END CONFIGURATION ---

    def handle(self, *args, **options):
        if not CustomUser.objects.filter(is_superuser=True).exists():
            self.stdout.write(self.style.WARNING(
                'No superuser found. Please create a superuser first: `python manage.py createsuperuser`'
            ))
            return

        self.stdout.write("🚀 Starting enhanced database seeding process...")
        
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

        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully with enhanced data! ✅'))

    def clean_database(self):
        """Deletes existing data to ensure a clean slate, preserving users."""
        self.stdout.write("🔥 Cleaning old data (excluding users)...")
        Payment.objects.all().delete()
        Booking.objects.all().delete()
        Expense.objects.all().delete()
        Trip.objects.all().delete()
        Customer.objects.filter(created_by__is_superuser=False).delete()


    def create_users(self):
        """Creates standard user roles if they don't exist."""
        self.stdout.write("👤 Creating user roles...")
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
        """Creates a large batch of fake customers."""
        self.stdout.write(f"👥 Creating {self.NUM_CUSTOMERS} customers...")
        fake = Faker()
        customers = [
            Customer(
                full_name=fake.name(),
                phone_number=fake.unique.phone_number(),
                email=fake.unique.email(),
                passport_number=fake.unique.bothify(text='?#########').upper(),
                passport_expiry_date=fake.date_between(start_date='+1y', end_date='+10y'),
                nationality=fake.country(),
                date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=70),
                created_by=random.choice(self.users.filter(role=CustomUser.Roles.AGENT))
            ) for _ in range(self.NUM_CUSTOMERS)
        ]
        Customer.objects.bulk_create(customers)
        self.customers = Customer.objects.all()

    def create_trips(self):
        """Creates a larger, more realistic set of trips with seasonal pricing."""
        self.stdout.write(f"✈️ Creating {self.NUM_TRIPS} realistic trips...")
        fake = Faker()
        trips = []

        for i in range(self.NUM_TRIPS):
            # Introduce seasonality and event-based logic
            is_ramadan_trip = i % 5 == 0  # Make every 5th trip a Ramadan trip
            is_hajj_trip = i % 10 == 0 # Make every 10th trip a Hajj trip
            
            base_price = Decimal(random.randrange(1200, 3500, 100))
            departure_dt = timezone.now() + timedelta(days=random.randint(-180, 500)) # Past and future trips
            duration = random.choice([7, 10, 14, 15, 20, 25])
            
            trip_name = f"{random.choice(['Economy', 'Standard', 'Comfort'])} Umrah"
            
            if is_ramadan_trip:
                # Simulate Ramadan trips in the future
                ramadan_start = date(timezone.now().year + 1, 3, 1) # Approximate
                departure_dt = timezone.make_aware(datetime.combine(ramadan_start, datetime.min.time())) + timedelta(days=random.randint(-5, 5))
                base_price *= Decimal('2.5') # Ramadan trips are expensive
                trip_name = f"Ramadan Special Umrah {departure_dt.year}"
                duration = random.choice([15, 25, 30])

            if is_hajj_trip:
                 # Simulate Hajj trips in the future
                hajj_start = date(timezone.now().year + 1, 6, 15) # Approximate
                departure_dt = timezone.make_aware(datetime.combine(hajj_start, datetime.min.time())) + timedelta(days=random.randint(-2, 2))
                base_price *= Decimal('4.0') # Hajj is the most expensive
                trip_name = f"Premium Hajj {departure_dt.year}"
                duration = random.choice([20, 25, 30])

            # Adjust price based on duration
            price_per_person = base_price + (duration * Decimal('50'))

            # Determine status
            status = Trip.Status.SCHEDULED if departure_dt > timezone.now() else Trip.Status.COMPLETED
            if status == Trip.Status.SCHEDULED and random.random() > 0.3:
                status = Trip.Status.ACTIVE

            trips.append(Trip(
                name=f"{trip_name} - {i+1}",
                description=fake.paragraph(nb_sentences=3),
                departure_date=departure_dt,
                return_date=departure_dt + timedelta(days=duration),
                total_seats=random.randint(40, 150),
                price_per_person=price_per_person,
                status=status,
                hotel_details=f"{random.choice(['3-star', '4-star', '5-star'])} hotel: {fake.company()}",
                flight_details=f"Flight with {fake.company()} Airlines"
            ))
        Trip.objects.bulk_create(trips)
        self.active_trips = Trip.objects.filter(status__in=[Trip.Status.SCHEDULED, Trip.Status.ACTIVE])

    def create_bookings_and_payments(self):
        """Creates a large number of bookings and payments."""
        self.stdout.write(f"🧾 Creating {self.NUM_BOOKINGS} bookings and payments...")
        if not self.active_trips.exists():
            self.stdout.write(self.style.WARNING("No active trips to create bookings for."))
            return
            
        bookings = []
        used_customer_trip_pairs = set()

        for _ in range(self.NUM_BOOKINGS):
            trip = random.choice(self.active_trips)
            customer = random.choice(self.customers)

            if (customer.id, trip.id) in used_customer_trip_pairs or trip.available_seats <= 0:
                continue
            
            booking = Booking(
                customer=customer,
                trip=trip,
                created_by=random.choice(self.users.filter(role=CustomUser.Roles.AGENT)),
                total_amount=trip.price_per_person,
                status=random.choice([
                    Booking.Status.PENDING_DOCUMENTS, Booking.Status.PENDING_PAYMENT,
                    Booking.Status.CONFIRMED, Booking.Status.FULLY_PAID
                ])
            )
            bookings.append(booking)
            used_customer_trip_pairs.add((customer.id, trip.id))
        
        Booking.objects.bulk_create(bookings)
        
        payments = []
        for booking in Booking.objects.all():
            if booking.status == Booking.Status.CONFIRMED:
                random_ratio = Decimal(str(random.uniform(0.2, 0.8)))
                amount = round(booking.total_amount * random_ratio, 2)
                payments.append(self.create_payment_instance(booking, amount))
            elif booking.status == Booking.Status.FULLY_PAID:
                payments.append(self.create_payment_instance(booking, booking.total_amount))
        
        Payment.objects.bulk_create(payments)

    def create_payment_instance(self, booking, amount):
        """Helper to create a Payment object instance."""
        return Payment(
            booking=booking, amount_paid=amount,
            payment_date=timezone.now().date() - timedelta(days=random.randint(1, 30)),
            payment_method=random.choice(Payment.PaymentMethod.choices)[0],
            recorded_by=random.choice(self.users.filter(role__in=[CustomUser.Roles.AGENT, CustomUser.Roles.ACCOUNTANT]))
        )

    def create_expenses(self):
        """Creates random expenses for trips."""
        self.stdout.write("💸 Creating expenses for trips...")
        expenses = []
        for trip in Trip.objects.all():
            for _ in range(random.randint(3, 8)):
                # Expenses should be a fraction of the total expected revenue
                expected_revenue = trip.total_seats * trip.price_per_person
                expense_amount = expected_revenue * Decimal(str(random.uniform(0.01, 0.05)))
                expenses.append(Expense(
                    trip=trip,
                    description=random.choice(["Hotel Booking", "Flight Tickets", "Transportation", "Visa Fees", "Catering", "Marketing"]),
                    amount=round(expense_amount, 2),
                    expense_date=trip.departure_date.date() - timedelta(days=random.randint(5, 45))
                ))
        Expense.objects.bulk_create(expenses)