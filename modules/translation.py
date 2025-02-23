# translation.py

from config import get_openai_api_key
from openai import OpenAI
import requests
from bs4 import BeautifulSoup

# Create the OpenAI client instance with your API key
client = OpenAI(api_key=get_openai_api_key())

def split_text(text, max_length=3000):
    """
    Splits text into smaller chunks so that each chunk
    stays within a specified maximum length (e.g., 3000 characters).
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


def extract_original_text(url):
    """
    Fetches the raw HTML from a URL, removes common non-text elements
    like <script> and <style>, then returns a clean string of text.
    """

    # Set a common browser-like User-Agent
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.114 Safari/537.36"
        )
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an error if the request failed

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove script and style elements to reduce clutter
    for element in soup(["script", "style"]):
        element.extract()

    # Extract all text; separate blocks with a space
    raw_text = soup.get_text(separator=" ")
    # Reduce extra whitespace
    clean_text = " ".join(raw_text.split())

    return clean_text


def extract_and_translate(url):
    """
    Extracts the raw text from a webpage and translates it using GPT-4.
    Keeps factual integrity and structure intact.
    """
    # 1. Get the original text
    original_text = extract_original_text(url)

    # 2. Split the text for more manageable GPT-4 calls
    chunks = split_text(original_text)

    translated_chunks = []
    for chunk in chunks:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional journalist specializing in medical technology. "
                        "Translate the article from English to Spanish (if applicable) while maintaining factual integrity. "
                        "Do NOT add any information not explicitly stated in the original text. "
                        "Do NOT fabricate sources, statistics, or claims. "
                        "Maintain the structure and paragraph separation of the original content. "
                        "Use titles, headings, and bullet points where appropriate. "
                        "Ensure the translation is accurate, professional, and informative. "
                        "Cite sources where necessary. "
                        "Credit authors and publications where applicable."
                    )
                },
                {"role": "user", "content": chunk}
            ],
        )
        translated_text = response.choices[0].message.content
        translated_chunks.append(translated_text)

    # 3. Combine all translated chunks
    final_translation = "\n\n".join(translated_chunks)

    return final_translation
