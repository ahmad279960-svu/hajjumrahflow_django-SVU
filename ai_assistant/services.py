# ai_assistant/services.py

import requests
import json
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class OpenRouterService:
    """
    A service to interact with the OpenRouter.ai API for AI completions.
    This version is updated to match OpenRouter's recommended request format.
    """
    API_URL = "https://openrouter.ai/api/v1/chat/completions"
    
    # Define site details as recommended by OpenRouter for API calls
    SITE_URL = "http://127.0.0.1:8000" # Use your actual domain in production
    SITE_TITLE = "HajjUmrahFlow"

    @staticmethod
    def get_ai_response(question: str) -> str:
        api_key = settings.OPENROUTER_API_KEY
        if not api_key:
            return str(_("AI service is not configured. API key is missing."))

        system_prompt = (
            "You are a helpful assistant for a travel agency specializing in Hajj and Umrah trips. "
            "Your name is 'HajjUmrahFlow Assistant'. Provide concise, helpful, and respectful answers "
            "related to pilgrimage, travel tips, and best practices. "
            "Always answer in the same language as the user's question."
        )

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": OpenRouterService.SITE_URL, 
            "X-Title": OpenRouterService.SITE_TITLE,
        }

        # --- MODEL SELECTION ---
        # This is where you choose the model.
        # The model is now set to the user-selected deepseek-chat-v3.
        payload = {
            "model": "google/gemma-3-27b-it:free",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ]
        }
        # --- END OF MODEL SELECTION ---

        try:
            response = requests.post(
                url=OpenRouterService.API_URL,
                headers=headers,
                data=json.dumps(payload),
                timeout=30
            )

            response.raise_for_status()
            
            data = response.json()
            return data['choices'][0]['message']['content']

        except requests.exceptions.HTTPError as http_err:
            error_details = response.json().get('error', {}).get('message', response.text)
            print(f"HTTP error occurred: {http_err} - Details: {error_details}")
            if response.status_code == 401:
                return str(_("Authentication error. Please check your OpenRouter API key."))
            return str(_(f"An API error occurred: {response.status_code}"))
            
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to OpenRouter API: {e}")
            return str(_("Sorry, I am having trouble connecting to the AI service. Please check your network connection."))
            
        except (KeyError, IndexError) as e:
            print(f"Unexpected API response format: {e}")
            return str(_("Sorry, I received an unexpected response from the AI service."))