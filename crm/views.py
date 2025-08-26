# crm/views.py

from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.contrib import messages

from .models import Customer
from .forms import CustomerForm

class CustomerListView(LoginRequiredMixin, ListView):
    """
    Displays a paginated list of customers.
    Includes a search functionality that filters by name, phone, or passport number.
    This fulfills requirement 003-FR-CRM.
    """
    model = Customer
    template_name = 'crm/customer_list.html'
    context_object_name = 'customers'
    paginate_by = 15 # Show 15 customers per page

    def get_queryset(self):
        """
        Overrides the default queryset to implement search functionality.
        """
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            # The Q object allows for complex queries with OR conditions.
            queryset = queryset.filter(
                Q(full_name__icontains=query) |
                Q(phone_number__icontains=query) |
                Q(passport_number__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        """
        Adds the search query back to the context to display it in the template.
        """
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context

class CustomerDetailView(LoginRequiredMixin, DetailView):
    """
    Displays the detailed profile of a single customer.
    The template for this view will show related documents, communication logs,
    and booking history as per requirements 004-FR-CRM and 005-FR-CRM.
    """
    model = Customer
    template_name = 'crm/customer_detail.html'
    context_object_name = 'customer'
    
    # In a real implementation, we would add the related objects
    # to the context here if more complex queries were needed.
    # For now, the template can access them directly via the customer object.


class CustomerCreateView(LoginRequireduin, CreateView):
    """
    Handles the creation of a new customer record using the CustomerForm.
    """
    model = Customer
    form_class = CustomerForm
    template_name = 'crm/customer_form.html'
    success_url = reverse_lazy('crm:customer-list')

    def form_valid(self, form):
        """
        Automatically sets the 'created_by' field to the current user
        before saving the new customer.
        """
        form.instance.created_by = self.request.user
        messages.success(self.request, _("Customer created successfully."))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _("Create New Customer")
        return context


class CustomerUpdateView(LoginRequiredMixin, UpdateView):
    """
    Handles the updating of an existing customer record.
    """
    model = Customer
    form_class = CustomerForm
    template_name = 'crm/customer_form.html'
    
    def get_success_url(self):
        """
        Redirects back to the customer's detail page upon successful update.
        """
        messages.success(self.request, _("Customer details updated successfully."))
        return reverse_lazy('crm:customer-detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _("Update Customer")
        return context