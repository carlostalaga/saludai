# config.py

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_openai_api_key():
    """
    Retrieve the OpenAI API key from environment variables.
    Raises an error if OPENAI_API_KEY is not found.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set in the environment variables.")
    return api_key

def get_wordpress_credentials():
    """
    Retrieve WordPress credentials and URLs from environment variables.
    Raises an error if any are missing.
    """
    wp_url = os.getenv("WP_URL")
    media_url = os.getenv("MEDIA_URL")
    wp_user = os.getenv("WP_USER")
    wp_app_password = os.getenv("WP_APP_PASSWORD")

    if not all([wp_url, media_url, wp_user, wp_app_password]):
        raise ValueError("One or more WordPress environment variables are not set.")
    
    return {
        "wp_url": wp_url,
        "media_url": media_url,
        "wp_user": wp_user,
        "wp_app_password": wp_app_password
    }

def get_model_for_module(module_name):
    """
    Retrieve the preferred OpenAI model for a given module.
    """
    model_mapping = {
        "translation": "gpt-4",
        "moderation": "gpt-4",
        "fact_check": "gpt-4",
        "formatting": "gpt-3.5-turbo",
        "seo": "gpt-3.5-turbo",
        # Note: thumbnail.py uses DALL-E (client.images.generate), not a GPT chat model.
    }
    return model_mapping.get(module_name, "gpt-3.5-turbo")  # Default to gpt-3.5-turbo
