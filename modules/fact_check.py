#fact_check.py

import openai

openai.api_key = "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"

client = openai.OpenAI(api_key=openai.api_key)

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
