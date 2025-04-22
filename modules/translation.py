# translation.py

from config import get_openai_api_key, get_model_for_module
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
    Translates the provided text using the preferred GPT model for translation.
    """
    model = get_model_for_module("translation")

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
        "--- IMPORTANT RULE FOR REFERENCES AND CITATIONS ---\n"
        "Remove ALL references to footnotes, endnotes, or citations in square brackets [86], parentheses (86), or similar formats. "
        "DO NOT include any of these reference markers in your translation. Simply translate the content without "
        "these citation markers. For example, \"This is a fact [82].\" should be translated as just \"This is a fact.\" in Spanish.\n\n"
        "--- IMPORTANT RULE FOR TECHNICAL TERMS WITH ACRONYMS ---\n"
        "Pay close attention to technical terms presented in the format 'Full Name (ACRONYM)' or 'Full Name (ACRONYMs)', like 'Artificial Intelligence (AI)' or 'Large Language Models (LLMs)'.\n"
        "When you encounter such a technical term in English with its acronym, follow these rules strictly:\n"
        "1. ALWAYS keep the acronym exactly as it appears in the original English text. Never translate acronyms.\n"
        "2. For the mention of a technical term with an acronym:\n"
        "   a. Write the Spanish translation of the full name.\n"
        "   b. Immediately after the Spanish translation, add parentheses containing:\n"
        "      i. The original English full name.\n"
        "      ii. A space, a hyphen, and another space (' - ').\n"
        "      iii. The original English acronym.\n"
        "   Example: when 'Machine Learning (ML)' appears, translate it as: Aprendizaje Automático (Machine Learning - ML).\n"
        "   Example: when 'Convolutional Neural Networks (CNN)' appears, translate it as: Redes Neuronales Convolucionales (Convolutional Neural Networks - CNN).\n"
        "   Example: when 'Large Language Models (LLMs)' appears, translate it as: Modelos Lingüísticos Grandes (Large Language Models - LLMs).\n"
        "   Example: when 'Artificial Intelligence (AI)' appears, translate it as: Inteligencia Artificial (Artificial Intelligence - AI).\n"
        "3. NEVER translate the acronym itself - 'ML' must remain 'ML', not 'AA'.\n"
        "4. If the rules are not followed, the output will be considered invalid.\n"
        "--- END OF RULES ---"
    )

    # 2. Translate chunk by chunk
    print(f"ℹ️ Text length: {len(text)} characters. Splitting into {len(chunks)} chunks.") # Added info
    for i, chunk in enumerate(chunks): # Added enumerate for index
        try:
            print(f"⚙️ Processing translation chunk {i+1}/{len(chunks)}...") # Added print statement
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
            translated_text = response.choices[0].message.content
            translated_chunks.append(translated_text)
        except Exception as e:
            print(f"❌ Error during translation chunk {i+1}: {e}") # Updated error message
            # Optionally append original chunk or handle error
            translated_chunks.append(f"[Translation Error in chunk {i+1}]" ) # Updated error placeholder

    # 3. Combine all translated chunks
    full_translation = "\n\n".join(translated_chunks)

    # 4. Post-processing removed - Relying on prompt

    return full_translation