# reports/services/manifest_generator.py

from django.http import HttpResponse
from django.template.loader import render_to_string
from openpyxl import Workbook
from weasyprint import HTML

from bookings.models import Booking

class ManifestGenerator:
    """
    A service class responsible for generating passenger manifests for a trip.
    Fulfills requirement 001-FR-REP.
    """
    def __init__(self, trip):
        self.trip = trip
        self.bookings = Booking.objects.filter(trip=self.trip).exclude(status='cancelled').select_related('customer')

    def generate_excel(self):
        """
        Generates a passenger manifest as an Excel file.
        """
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = f'attachment; filename="manifest_{self.trip.name}.xlsx"'

        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = 'Passenger Manifest'

        # Define headers
        headers = ['#', 'Full Name', 'Passport Number', 'Nationality', 'Date of Birth']
        worksheet.append(headers)

        # Populate data
        for i, booking in enumerate(self.bookings, 1):
            customer = booking.customer
            row = [i, customer.full_name, customer.passport_number, customer.nationality, customer.date_of_birth]
            worksheet.append(row)

        workbook.save(response)
        return response

    def generate_pdf(self):
        """
        Generates a passenger manifest as a PDF file.
        """
        context = {
            'trip': self.trip,
            'bookings': self.bookings,
        }
        html_string = render_to_string('reports/pdf/manifest_template.html', context)
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="manifest_{self.trip.name}.pdf"'

        HTML(string=html_string).write_pdf(response)
        return response