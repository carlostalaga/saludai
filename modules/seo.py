# seo.py

import json
from config import get_openai_api_key, get_model_for_module
from openai import OpenAI

# Create the OpenAI client instance with your API key
client = OpenAI(api_key=get_openai_api_key())

# Only the first part of the article is needed to determine category and write an excerpt
SEO_INPUT_MAX_CHARS = 2000

def generate_seo_data(content):
    """
    Returns (excerpt, category_name) in a single API call using only the first
    2000 chars of the article — excerpt and category don't need the full text.
    """
    model = get_model_for_module("seo")
    truncated = content[:SEO_INPUT_MAX_CHARS]

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You will receive a Spanish health article. "
                        "Return a JSON object with exactly two keys:\n"
                        "- \"excerpt\": a short, engaging meta description under 160 characters\n"
                        "- \"category\": the most relevant category from: 'Medicina Estetica', "
                        "'Inteligencia Artificial', 'Tecnologia Medica', 'Fitness', 'Biotecnologia', 'Economia'\n"
                        "Return only valid JSON, no extra text."
                    )
                },
                {"role": "user", "content": truncated}
            ],
        )
        result = json.loads(response.choices[0].message.content.strip())
        return result["excerpt"], result["category"]
    except Exception as e:
        print(f"❌ SEO data generation failed: {e}")
        return "", "Tecnologia Medica"


# Keep legacy functions for backward compatibility
def generate_excerpt(content):
    excerpt, _ = generate_seo_data(content)
    return excerpt

def assign_category(content):
    _, category = generate_seo_data(content)
    return category
