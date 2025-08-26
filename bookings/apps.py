# bookings/apps.py

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class BookingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bookings'
    verbose_name = _('Bookings Management')

    def ready(self):
        """
        This method is called when the app is ready.
        It's the standard place to import signals to ensure they are connected.
        """
        import bookings.signals