# bookings/signals.py

import requests
import os
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Booking, Payment

# A simple logging function for development
def log_webhook_attempt(url, payload, response):
    """Logs the outcome of a webhook attempt for debugging."""
    if settings.DEBUG:
        print(f"--- Webhook Attempt ---")
        print(f"URL: {url}")
        print(f"Payload: {payload}")
        if response:
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text[:200]}") # Print first 200 chars
        else:
            print("Status: FAILED (Request exception)")
        print(f"-----------------------")


@receiver(post_save, sender=Booking)
def trigger_new_booking_workflow(sender, instance, created, **kwargs):
    """
    Sends a webhook to n8n when a new booking is created.
    This fulfills requirement 004-FR-BOK.
    """
    if created: # Only trigger on creation
        webhook_url = os.getenv('N8N_NEW_BOOKING_WEBHOOK_URL')
        if not webhook_url:
            if settings.DEBUG:
                print("WARNING: N8N_NEW_BOOKING_WEBHOOK_URL is not set. Skipping webhook.")
            return

        payload = {
            'booking_id': instance.id,
            'customer_id': instance.customer.id,
            'trip_id': instance.trip.id,
        }
        
        try:
            response = requests.post(webhook_url, json=payload, timeout=5)
            log_webhook_attempt(webhook_url, payload, response)
        except requests.exceptions.RequestException as e:
            log_webhook_attempt(webhook_url, payload, None)
            print(f"ERROR: Webhook request failed: {e}")

@receiver(post_save, sender=Payment)
def handle_new_payment(sender, instance, created, **kwargs):
    """
    Handles logic after a payment is saved.
    1. Updates the associated booking's status. (Requirement 002-FR-FIN)
    2. Sends a webhook to n8n to trigger a receipt workflow. (Requirement 003-FR-FIN)
    """
    booking = instance.booking
    
    # 1. Update Booking Status
    if booking.balance_due <= 0:
        booking.status = Booking.Status.FULLY_PAID
    elif booking.status == Booking.Status.PENDING_PAYMENT:
        booking.status = Booking.Status.CONFIRMED
    booking.save()

    # 2. Trigger Receipt Webhook (only on creation)
    if created:
        webhook_url = os.getenv('N8N_PAYMENT_RECEIPT_WEBHOOK_URL')
        if not webhook_url:
            if settings.DEBUG:
                print("WARNING: N8N_PAYMENT_RECEIPT_WEBHOOK_URL is not set. Skipping webhook.")
            return

        payload = {
            'payment_id': instance.id,
            'booking_id': booking.id,
            'customer_id': booking.customer.id,
        }
        
        try:
            response = requests.post(webhook_url, json=payload, timeout=5)
            log_webhook_attempt(webhook_url, payload, response)
        except requests.exceptions.RequestException as e:
            log_webhook_attempt(webhook_url, payload, None)
            print(f"ERROR: Webhook request failed: {e}")