# seo.py

from config import get_openai_api_key, get_model_for_module
from openai import OpenAI

# Create the OpenAI client instance with your API key
client = OpenAI(api_key=get_openai_api_key())

def generate_excerpt(content):
    """
    Creates a short excerpt (meta description) for SEO and previews using the preferred GPT model.
    """
    model = get_model_for_module("seo")
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "Generate a short, engaging excerpt (meta description) summarizing the following content. "
                    "Make it informative while keeping it under 160 characters for SEO purposes."
                )
            },
            {"role": "user", "content": content}
        ],
    )
    return response.choices[0].message.content.strip()

def assign_category(content):
    """
    Suggests an appropriate category for the article based on its topic using the preferred GPT model.
    """
    model = get_model_for_module("seo")
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "Analyze the following text and suggest the most relevant category for it. "
                    "Choose from: 'Medicina Estetica', 'Inteligencia Artificial', 'Tecnologia Medica', "
                    "'Fitness', 'Biotecnologia' or 'Economia'."
                )
            },
            {"role": "user", "content": content}
        ],
    )
    return response.choices[0].message.content.strip()
