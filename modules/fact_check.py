#fact_check.py

import openai
from config import get_openai_api_key

# Set the OpenAI API key
openai.api_key = get_openai_api_key()

def fact_check_translation(original_text, translated_text):
    """AI compares its own translation with the original to ensure factual accuracy."""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": 
                "Compare the following two texts. The first is in English (original), and the second is in Spanish (translated). "
                "Ensure the Spanish version correctly reflects the English version while maintaining the translation. "
                "Do NOT rewrite or translate the Spanish version back into English. "
                "Check for any factual inconsistencies, missing details, or hallucinated information. "
                "Ensure the translation remains accurate and fact-based, without exaggerations or omissions. "
                "Only make factual corrections while keeping the final output in Spanish."
                "Remove any part of other articles or advertising that may have been included in the translation."
            },
            {"role": "user", "content": f"Original: {original_text} \n\n Translation: {translated_text}"}
        ]
    )

    return response.choices[0].message.content  # ✅ No incorrect unpacking
