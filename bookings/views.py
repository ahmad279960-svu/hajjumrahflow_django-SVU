# bookings/views.py

from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, FormView
from django.views.generic.base import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from .models import Booking, Payment, Trip, Customer
from .forms import PaymentForm, BookingForm

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
        # Add filtering logic here if needed, e.g., by trip or status
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
    http_method_names = ['post'] # This view only accepts POST requests

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
        # To display the errors, we redirect back. The state is lost, but it's simpler
        # than re-rendering the detail page from this view.
        return redirect('bookings:booking-detail', pk=self.kwargs.get('booking_pk'))

# --- Booking Creation Wizard ---

class BookingCreateWizardView(LoginRequiredMixin, TemplateView):
    """
    A view that orchestrates the multi-step booking creation wizard.
    It uses the session to store data between steps.
    """
    def get(self, request, *args, **kwargs):
        # Determine which step to show
        step = kwargs.get('step', 1)
        if step == 1:
            template_name = 'bookings/booking_wizard_step1_customer.html'
            context = {'customers': Customer.objects.all()} # Add search/pagination in a real app
        elif step == 2:
            template_name = 'bookings/booking_wizard_step2_trip.html'
            context = {'trips': Trip.objects.filter(status__in=['scheduled', 'active'])}
        elif step == 3:
            template_name = 'bookings/booking_wizard_step3_confirm.html'
            customer_id = request.session.get('booking_wizard_customer_id')
            trip_id = request.session.get('booking_wizard_trip_id')
            if not customer_id or not trip_id:
                messages.error(request, _("Session expired or data missing. Please start over."))
                return redirect(reverse('bookings:booking-create-step', kwargs={'step': 1}))
            
            context = {
                'customer': get_object_or_404(Customer, pk=customer_id),
                'trip': get_object_or_404(Trip, pk=trip_id),
            }
        else:
            return redirect(reverse('bookings:booking-create-step', kwargs={'step': 1}))
            
        return self.render_to_response(context, template_name=template_name)

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

            booking = Booking.objects.create(
                customer_id=customer_id,
                trip_id=trip_id,
                created_by=request.user,
                total_amount=trip.price_per_person,
                status=Booking.Status.PENDING_DOCUMENTS # Or PENDING_PAYMENT
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
    An HTMX-powered view to check for available seats on a trip in real-time.
    This fulfills requirement 002-FR-BOK.
    """
    def get(self, request, *args, **kwargs):
        trip_id = request.GET.get('trip_id')
        context = {'trip_selected': False}
        if trip_id:
            trip = get_object_or_404(Trip, pk=trip_id)
            context['seats_available'] = trip.available_seats > 0
            context['trip_selected'] = True
        return self.render_to_response(context, template_name='bookings/htmx/check_seat_availability.html')

    def render_to_response(self, context, **response_kwargs):
        # A helper method for rendering, though it's simple enough to be in get()
        from django.template.loader import render_to_string
        from django.http import HttpResponse
        html = render_to_string(response_kwargs['template_name'], context, request=self.request)
        return HttpResponse(html)