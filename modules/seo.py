# seo.py

import openai
from config import get_openai_api_key

# Set the OpenAI API key
openai.api_key = get_openai_api_key()

def generate_seo_title(content):
    """Generates an SEO-friendly article title based on the translated content, max 60 characters."""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": 
                "Generate a compelling SEO-friendly article title based on the following text. "
                "Keep it under 60 characters while keeping it engaging and keyword-rich."},
            {"role": "user", "content": content}
        ]
    )

    # Ensure the title does not exceed 60 characters
    seo_title = response.choices[0].message.content.strip()
    return seo_title[:60]  # ✅ Trim title if it exceeds 60 characters


def generate_excerpt(content):
    """Creates a short excerpt (meta description) for SEO and previews."""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": 
                "Generate a short, engaging excerpt (meta description) summarizing the following content. "
                "Make it informative while keeping it under 160 characters for SEO purposes."},
            {"role": "user", "content": content}
        ]
    )
    return response.choices[0].message.content.strip()

def assign_category(content):
    """Suggests an appropriate category for the article based on its topic."""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": 
                "Analyze the following text and suggest the most relevant category for it. "
                "Choose from: 'Medicina Estetica', 'Inteligencia Artificial', Tecnologia Medica', 'Fitness', 'Biotecnologia' or 'Economia'."},
            {"role": "user", "content": content}
        ]
    )
    return response.choices[0].message.content.strip()