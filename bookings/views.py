# bookings/views.py

from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, FormView
from django.views.generic.base import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse

from .models import Booking, Payment
from .forms import PaymentForm
from trips.models import Trip
from crm.models import Customer

class BookingListView(LoginRequiredMixin, ListView):
    """
    Displays a list of all bookings with filtering capabilities.
    """
    model = Booking
    template_name = 'bookings/booking_list.html'
    context_object_name = 'bookings'
    paginate_by = 15

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related('customer', 'trip')


class BookingDetailView(LoginRequiredMixin, DetailView):
    """
    Displays the details of a single booking, including its payment history.
    Also provides a form to add a new payment.
    """
    model = Booking
    template_name = 'bookings/booking_detail.html'
    context_object_name = 'booking'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['payment_form'] = PaymentForm()
        context['payments'] = self.object.payments.all().order_by('-payment_date')
        return context

class AddPaymentView(LoginRequiredMixin, FormView):
    """
    Handles the submission of the payment form.
    """
    form_class = PaymentForm
    http_method_names = ['post']

    def form_valid(self, form):
        booking = get_object_or_404(Booking, pk=self.kwargs.get('booking_pk'))
        payment = form.save(commit=False)
        payment.booking = booking
        payment.recorded_by = self.request.user
        payment.save()
        messages.success(self.request, _("Payment recorded successfully."))
        return redirect('bookings:booking-detail', pk=booking.pk)

    def form_invalid(self, form):
        messages.error(self.request, _("There was an error in the form. Please correct it and try again."))
        return redirect('bookings:booking-detail', pk=self.kwargs.get('booking_pk'))

# --- Booking Creation Wizard ---

class BookingCreateWizardView(LoginRequiredMixin, View):
    """
    A view that orchestrates the multi-step booking creation wizard.
    It uses the session to store data between steps.
    """
    def get(self, request, *args, **kwargs):
        step = kwargs.get('step', 1)

        if step == 1:
            # Clear any previous wizard data from the session
            request.session.pop('booking_wizard_customer_id', None)
            request.session.pop('booking_wizard_trip_id', None)
            template_name = 'bookings/booking_wizard_step1_customer.html'
            context = {'customers': Customer.objects.all()}
        elif step == 2:
            template_name = 'bookings/booking_wizard_step2_trip.html'
            context = {'trips': Trip.objects.filter(status__in=['scheduled', 'active'])}
        elif step == 3:
            customer_id = request.session.get('booking_wizard_customer_id')
            trip_id = request.session.get('booking_wizard_trip_id')
            if not customer_id or not trip_id:
                messages.error(request, _("Session expired or data missing. Please start over."))
                return redirect(reverse('bookings:booking-create-step', kwargs={'step': 1}))
            
            template_name = 'bookings/booking_wizard_step3_confirm.html'
            context = {
                'customer': get_object_or_404(Customer, pk=customer_id),
                'trip': get_object_or_404(Trip, pk=trip_id),
            }
        else:
            return redirect(reverse('bookings:booking-create-step', kwargs={'step': 1}))
            
        return render(request, template_name, context)

    def post(self, request, *args, **kwargs):
        step = kwargs.get('step', 1)
        if step == 1:
            request.session['booking_wizard_customer_id'] = request.POST.get('customer_id')
            return redirect(reverse('bookings:booking-create-step', kwargs={'step': 2}))
        elif step == 2:
            request.session['booking_wizard_trip_id'] = request.POST.get('trip_id')
            return redirect(reverse('bookings:booking-create-step', kwargs={'step': 3}))
        elif step == 3:
            customer_id = request.session.get('booking_wizard_customer_id')
            trip_id = request.session.get('booking_wizard_trip_id')
            trip = get_object_or_404(Trip, pk=trip_id)

            if trip.available_seats <= 0:
                messages.error(request, _("Sorry, no seats are available for this trip."))
                return redirect(reverse('bookings:booking-create-step', kwargs={'step': 2}))

            booking = Booking.objects.create(
                customer_id=customer_id,
                trip_id=trip_id,
                created_by=request.user,
                total_amount=trip.price_per_person,
                status=Booking.Status.PENDING_DOCUMENTS
            )
            # Clear session data
            del request.session['booking_wizard_customer_id']
            del request.session['booking_wizard_trip_id']
            
            messages.success(request, _("Booking created successfully!"))
            return redirect('bookings:booking-detail', pk=booking.pk)
        
        return redirect(reverse('bookings:booking-list'))

# --- HTMX View ---

class CheckSeatAvailabilityView(LoginRequiredMixin, View):
    """
    An HTMX-powered view that checks for available seats on a trip.
    FIX: This view now returns a JSON response, which is more robust for JavaScript to handle.
    """
    def get(self, request, *args, **kwargs):
        trip_id = request.GET.get('trip_id')
        if not trip_id:
            return JsonResponse({'error': 'No trip_id provided'}, status=400)
        
        try:
            trip = Trip.objects.get(pk=trip_id)
            seats_available = trip.available_seats > 0
            return JsonResponse({
                'trip_id': trip.id,
                'seats_available': seats_available
            })
        except (Trip.DoesNotExist, ValueError, TypeError):
            return JsonResponse({'error': 'Invalid trip_id'}, status=404)