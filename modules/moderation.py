# moderation.py

from config import get_openai_api_key
from openai import OpenAI

# Create the OpenAI client instance with your API key
client = OpenAI(api_key=get_openai_api_key())

def moderate_content(text):
    """
    Reviews a Spanish medical article (translated from English) for factual accuracy.
    - Retains the entire Spanish text, preserving paragraph structure.
    - Removes or flags hallucinations, fabricated claims, or misleading info.
    - If a medical claim has no references, label it as an expert opinion.
    - Avoid rewriting or summarizing the text.
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are reviewing a Spanish medical article that was originally translated from English. "
                    "Your task is to ensure factual accuracy without altering the Spanish language or rewriting content. "
                    "Retain the Spanish text exactly as is—preserve structure, paragraphs, headings, and style. "
                    "Remove or mark (with minimal changes) any hallucinations, fabricated claims, or misleading medical information "
                    "that was not in the original text. "
                    "If a medical claim lacks proper attribution or references, clearly label it as an expert opinion rather than established fact. "
                    "Do not summarize, do not revert to English, and do not omit any valid text. "
                    "Return only the updated Spanish text, with minimal necessary edits to questionable sections. "
                    "If everything is valid, simply return the text unchanged."
                )
            },
            {
                "role": "user",
                "content": text
            }
        ],
    )

    return response.choices[0].message.content
