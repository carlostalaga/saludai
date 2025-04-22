# fact_check.py

from config import get_openai_api_key, get_model_for_module
from openai import OpenAI

client = OpenAI(api_key=get_openai_api_key())

def fact_check_translation(original_text, translated_text):
    """
    AI compares the Spanish translation with the original English text
    and returns a final, fact-checked Spanish version (no English summary).
    """
    model = get_model_for_module("fact_check") # Use the function to get the model

    response = client.chat.completions.create(
        model=model, # Use the dynamically selected model
        messages=[
            {
                "role": "system",
                "content": (
                    "You are verifying a Spanish translation of an English text. "
                    "You will receive two versions: first the English (original), then the Spanish (translated). "
                    "Perform a side-by-side comparison for factual accuracy, missing details, or hallucinations. "
                    "Your final output must be the corrected Spanish text ONLY, preserving paragraphs and structure. "
                    "Do not include commentary or summary in English. "
                    "Do not re-translate everything back to English. "
                    "If the Spanish text is already fully accurate, return it verbatim. "
                    "Otherwise, make only minimal corrections in Spanish where you find factual or translational errors."
                )
            },
            {
                "role": "user",
                "content": (
                    f"**Original (English)**:\n{original_text}\n\n"
                    f"**Translated (Spanish)**:\n{translated_text}"
                )
            }
        ],
    )

    # This should now be purely Spanish text (with minimal corrections).
    return response.choices[0].message.content
