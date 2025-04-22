# moderation.py

from config import get_openai_api_key, get_model_for_module
from openai import OpenAI

# Create the OpenAI client instance with your API key
client = OpenAI(api_key=get_openai_api_key())

def split_text(text, max_length=4000):
    """
    Splits text into smaller chunks so that each chunk
    stays within a specified maximum length (e.g., 4000 characters).
    """
    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        current_chunk.append(word)
        # If the chunk exceeds max_length, move on to the next
        if len(" ".join(current_chunk)) > max_length:
            chunks.append(" ".join(current_chunk))
            current_chunk = []

    # Add the remainder if there's anything left
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

def moderate_content(text):
    """
    Reviews a Spanish medical article (translated from English) for factual accuracy.
    - Retains the entire Spanish text, preserving paragraph structure.
    - Removes or flags hallucinations, fabricated claims, or misleading info.
    - If a medical claim has no references, label it as an expert opinion.
    - Avoid rewriting or summarizing the text.
    
    Handles texts of any length by splitting into chunks if necessary.
    """
    model = get_model_for_module("moderation") # Use the function to get the model
    
    # Check if text needs to be split (for GPT-4, ~8K tokens is roughly 32K characters)
    # Using a conservative 4000 character limit per chunk to stay well within limits
    if len(text) > 4000:
        chunks = split_text(text)
        moderated_chunks = []
        
        system_prompt = (
            "You are reviewing a chunk of a larger Spanish medical article that was originally translated from English. "
            "Your task is to ensure factual accuracy without altering the Spanish language or rewriting content. "
            "Retain the Spanish text exactly as is—preserve structure, paragraphs, headings, and style. "
            "Remove or mark (with minimal changes) any hallucinations, fabricated claims, or misleading medical information "
            "that was not in the original text. "
            "If a medical claim lacks proper attribution or references, clearly label it as an expert opinion rather than established fact. "
            "Do not summarize, do not revert to English, and do not omit any valid text. "
            "Return only the updated Spanish text, with minimal necessary edits to questionable sections. "
            "If everything is valid, simply return the text unchanged. "
            "Important: This is a chunk of a larger document, so process it independently without trying to connect it to other chunks."
        )
        
        # Process each chunk separately
        for i, chunk in enumerate(chunks):
            try:
                print(f"Processing moderation chunk {i+1}/{len(chunks)} ({len(chunk)} characters)")
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": system_prompt
                        },
                        {"role": "user", "content": chunk}
                    ],
                )
                moderated_chunk = response.choices[0].message.content
                moderated_chunks.append(moderated_chunk)
            except Exception as e:
                print(f"Error moderating chunk {i+1}: {e}")
                # Fallback: keep the original chunk
                moderated_chunks.append(chunk)
        
        # Combine all moderated chunks
        return "\n\n".join(moderated_chunks)
    else:
        # For shorter texts, process as before
        response = client.chat.completions.create(
            model=model,
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
