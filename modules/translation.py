# translation.py

import requests
from bs4 import BeautifulSoup

import openai
from config import get_openai_api_key

# Set the OpenAI API key
openai.api_key = get_openai_api_key()

def split_text(text, max_length=3000):
    """Splits text into chunks for better AI processing."""
    words = text.split()
    chunks = []
    chunk = []

    for word in words:
        chunk.append(word)
        if len(" ".join(chunk)) > max_length:
            chunks.append(" ".join(chunk))
            chunk = []

    if chunk:
        chunks.append(" ".join(chunk))

    return chunks

def extract_and_translate(url):
    """Extracts and translates an article, focusing on the main content and avoiding extraneous elements."""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    paragraphs = soup.find_all("p")
    content = " ".join([p.get_text() for p in paragraphs])

    chunks = split_text(content)

    translated_chunks = []
    for chunk in chunks:
        ai_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content":
                    "You are a professional journalist specializing in medical technology. "
                    "Translate the article maintaining factual integrity. "
                    "Do NOT add any information not explicitly stated in the original text. "
                    "Do NOT fabricate sources, statistics, or claims. "
                    "Maintain the structure and paragraph separation of the original article. "
                    "Use titles, headings, and bullet points where appropriate. "
                    "Ensure the translation is accurate, professional, and informative. "
                    "Cite sources where necessary. "
                    "Credit authors and publications where applicable."
                },
                {"role": "user", "content": chunk}
            ]
        )
        translated_chunks.append(ai_response.choices[0].message.content)

    return "\n\n".join(translated_chunks)  # Recombine chunks
