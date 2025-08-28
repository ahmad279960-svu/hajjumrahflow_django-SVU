# ai_assistant/views.py

import json
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .services import OpenRouterService

class AskAIView(LoginRequiredMixin, View):
    """
    Handles POST requests with a user's question and returns a JSON response
    from the AI service. Relies on CSRF token sent from the frontend.
    """
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            question = data.get('question')
            
            if not question:
                return JsonResponse({'error': 'No question provided.'}, status=400)

            # Get the response from the service
            ai_response = OpenRouterService.get_ai_response(question)
            
            return JsonResponse({'answer': ai_response})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON in request body.'}, status=400)