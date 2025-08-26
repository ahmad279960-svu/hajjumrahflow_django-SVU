# reports/views.py

from django.views.generic import TemplateView, View
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin

from trips.models import Trip
from .services.manifest_generator import ManifestGenerator
from .services.financial_reports import FinancialReportsGenerator
from users.mixins import ManagerRequiredMixin

class ReportDashboardView(LoginRequiredMixin, ManagerRequiredMixin, TemplateView):
    """
    Displays the main dashboard for generating reports.
    Restricted to Managers only.
    """
    template_name = 'reports/report_generation_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['trips'] = Trip.objects.all()
        # Fetching data for display on the dashboard itself
        context['overdue_payments'] = FinancialReportsGenerator.get_overdue_payments()
        return context

class GenerateManifestView(LoginRequiredMixin, ManagerRequiredMixin, View):
    """
    Handles the request to generate and download a passenger manifest.
    Restricted to Managers only.
    """
    def post(self, request, *args, **kwargs):
        trip_id = request.POST.get('trip_id')
        report_format = request.POST.get('format', 'pdf')
        trip = get_object_or_404(Trip, pk=trip_id)
        
        generator = ManifestGenerator(trip)

        if report_format == 'excel':
            return generator.generate_excel()
        else: # Default to PDF
            return generator.generate_pdf()

class TripProfitabilityView(LoginRequiredMixin, ManagerRequiredMixin, TemplateView):
    """
    Displays the profitability report for a selected trip.
    Restricted to Managers only.
    """
    template_name = 'reports/profitability_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        trip_id = self.request.GET.get('trip_id')
        if trip_id:
            trip = get_object_or_404(Trip, pk=trip_id)
            context['report_data'] = FinancialReportsGenerator.get_trip_profitability(trip)
        return context