# translation.py

from config import get_openai_api_key
from openai import OpenAI
import requests
from bs4 import BeautifulSoup
import re # Import regex module

# Create the OpenAI client instance with your API key
client = OpenAI(api_key=get_openai_api_key())

# Define known technical terms and their Spanish translations
# Add more terms to this dictionary as needed
# KNOWN_TECHNICAL_TERMS = { # Removed - Relying on prompt now
#     "Machine Learning (ML)": "Aprendizaje Automático",
#     "Convolutional Neural Networks (CNN)": "Redes Neuronales Convolucionales",
#     # Example: "Artificial Intelligence (AI)": "Inteligencia Artificial",
# }

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

def extract_and_translate(text):
    """
    Translates the provided text using GPT-4.
    Keeps factual integrity and structure intact.
    Handles the first occurrence of technical terms specially via prompt.
    """
    # 1. Split the text
    chunks = split_text(text)
    translated_chunks = []

    # System prompt (refined to handle first mention rule)
    system_prompt = (
        "You are a professional journalist specializing in medical technology. "
        "Translate the article from English to Spanish (if applicable) while maintaining factual integrity. "
        "Do NOT add any information not explicitly stated in the original text. "
        "Do NOT fabricate sources, statistics, or claims. "
        "Maintain the structure and paragraph separation of the original content. "
        "Use titles, headings, and bullet points where appropriate. "
        "Ensure the translation is accurate, professional, and informative. "
        "Cite sources where necessary. "
        "Credit authors and publications where applicable. \n\n"
        "--- IMPORTANT RULE FOR TECHNICAL TERMS WITH ACRONYMS ---\n"
        "When you encounter a technical term in English that has an acronym (like 'Machine Learning (ML)' or 'Convolutional Neural Networks (CNN)'), follow this specific rule for the *very first time* you translate it into Spanish within the entire article (not just this chunk):\n"
        "1. Write the original English term and its acronym exactly as it appears in the source.\n"
        "2. Add the Spanish phrase ' o ' (meaning 'or').\n"
        "3. Add the Spanish translation enclosed in single quotes ('').\n"
        "Example: The first time 'Machine Learning (ML)' appears, translate it as: Machine Learning (ML) o 'Aprendizaje Automático'.\n"
        "Example: The first time 'Convolutional Neural Networks (CNN)' appears, translate it as: Convolutional Neural Networks (CNN) o 'Redes Neuronales Convolucionales'.\n"
        "For *all subsequent* mentions of the same term (even in later chunks), use *only* the Spanish translation (e.g., 'Aprendizaje Automático') or just the acronym (e.g., 'ML'), whichever fits the context better. Do NOT repeat the English term after the first mention.\n"
        "--- END OF RULE ---"
    )

    # 2. Translate chunk by chunk
    for chunk in chunks:
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {"role": "user", "content": chunk}
                ],
            )
            translated_text = response.choices[0].message.content
            translated_chunks.append(translated_text)
        except Exception as e:
            print(f"Error during translation chunk: {e}")
            # Optionally append original chunk or handle error
            translated_chunks.append(f"[Translation Error: {chunk[:100]}...]" )

    # 3. Combine all translated chunks
    full_translation = "\n\n".join(translated_chunks)

    # 4. Post-processing removed - Relying on prompt

    return full_translation
