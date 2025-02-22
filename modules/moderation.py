# moderation.py

import openai
from config import get_openai_api_key

# Set the OpenAI API key
openai.api_key = get_openai_api_key()


def moderate_content(text):
    """Ensures content does not contain hallucinations, false medical claims, or speculative statements."""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": 
                "You are reviewing a translated medical article to ensure factual accuracy. "
                "Check for any hallucinations, fabricated claims, or misleading medical information. "
                "If a medical claim lacks proper attribution, indicate that it is an expert opinion rather than fact. "
                "Ensure that all information is derived from the original text and not speculative."},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content