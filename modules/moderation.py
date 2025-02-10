# moderation.py

import openai

openai.api_key = "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"
client = openai.OpenAI(api_key=openai.api_key)

def moderate_content(text):
    """Ensures content does not contain hallucinations, false medical claims, or speculative statements."""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": 
                "You are reviewing a translated medical article to ensure factual accuracy. "
                "Check for any hallucinations, fabricated claims, or misleading medical information. "
                "If a medical claim lacks proper attribution, indicate that it is an expert opinion rather than fact."
                "Ensure that all information is derived from the original text and not speculative."},
            {"role": "user", "content": text}
        ]
    )

    return response.choices[0].message.content
